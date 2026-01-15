import logging
from typing import List, Optional, Dict, Any
import re
import json
import asyncio


from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings
from .rag.factory import RAGFactory
from .rag.ingestion import IngestionService
from .rag.retrieval import RetrievalService
from llama_index.core.schema import NodeWithScore, TextNode

logger = logging.getLogger("ai_service")

class AIService:
    @classmethod
    def initialize(cls):
        """
        Initialize the RAG Factory (LlamaIndex components).
        """
        logger.info("Initializing RAG Factory...")
        # Accessing singletons triggers initialization
        RAGFactory.get_embedding_model()
        RAGFactory.get_llm()
        RAGFactory.get_index()
        logger.info("RAG Factory initialized successfully.")

    @classmethod
    def process_document(cls, text: str, metadata: dict = {}) -> List[dict]:
        """
        Delegates document processing to IngestionService.
        """
        try:
            logger.info("Processing document text...")
            nodes = IngestionService.process_text(text, metadata)
            
            # Convert Nodes back to list of dicts for backward compatibility/response format
            results = []
            for node in nodes:
                results.append({
                    "content": node.get_content(),
                    "embedding": node.embedding,
                    "metadata": node.metadata
                })
            return results
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise e

    @classmethod
    async def ask_llm(cls, question: str, context: str = "") -> Dict[str, Any]:
        """
        Delegates RAG query to RetrievalService.
        If context is provided (e.g. from Java), we bypass retrieval and use the LLM directly.
        """
        try:
            logger.info(f"Processing query: {question}")
            
            if context and len(context.strip()) > 10:
                logger.info("Using provided context for generation.")
                llm = RAGFactory.get_llm()
                
                # Context Injection: Current Date for relative time resolution
                import datetime
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                
                prompt = (
                    "Context information is below.\n"
                    "---------------------\n"
                    f"{context}\n"
                    "---------------------\n"
                    f"Reference Date: {today_str}\n\n"
                    f"Question: {question}\n\n"
                    "Answer the question based strictly on the provided context.\n"
                    "Guideline: Provide a DETAILED and COMPREHENSIVE answer based on the context.\n"
                    "1. Specificity: Include relevant details, technologies, and responsibilities. Avoid generic summaries.\n"
                    "2. Relevance: Include dates, durations, or metrics ONLY if they explicitly answer the question. Avoid irrelevant headers.\n"
                    "3. Calculation: If a timeline/duration is requested, calculate it explicitly using the Reference Date.\n"
                    "4. Language: Answer in the same language as the question (e.g. German for German questions)."
                )
                response = llm.complete(prompt)
                response_text = response.text
                
                return {
                    "answer": response_text,
                    "sources": ["Provided Context"]
                }

            # Fallback to internal Retrieval if no context provided
            query_engine = RetrievalService.get_query_engine()
            
            try:
                # Latency Budgeting: 60s timeout for local inference
                response = await asyncio.wait_for(query_engine.aquery(question), timeout=60.0)
            except asyncio.TimeoutError:
                logger.warning("Query timed out after 60s.")
                return {
                    "answer": "I'm sorry, I couldn't search the documents fast enough. Please try a simpler query.",
                    "sources": ["System: Timeout"]
                }
            
            # Extract Sources
            sources = []
            if response.source_nodes:
                for node in response.source_nodes[:5]:
                    fname = node.metadata.get('filename', 'Unknown')
                    page = node.metadata.get('page_label', '?')
                    score = f"{node.score:.2f}" if node.score else "?"
                    sources.append(f"📄 {fname} (p.{page}) [{score}]")
            
            return {
                "answer": str(response),
                "sources": sources
            }
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            return {"answer": "Error generating response.", "sources": []}

    @classmethod
    def rerank(cls, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """
        Optional reranking step.
        """
        try:
            # Returning top_k results as-is to minimize latency
            results = []
            for i, doc in enumerate(documents[:top_k]):
                results.append({
                    "content": doc,
                    "score": 1.0 - (i * 0.01) 
                })
            return results
        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            raise e
    
    @classmethod
    def extract_metadata(cls, text: str) -> dict:
        """
        Extracts metadata using the LLM.
        """
        try:
            llm = RAGFactory.get_llm()
            prompt_str = f"""
            Analyze the following document text and extract detailed metadata in strict JSON format.
            Do NOT include markdown formatting or backticks. Just the raw JSON object.
            
            Fields to extract:
            - "document_type": (String) e.g., "Invoice", "Resume", "Contract", "Letter", "Report"
            - "category": (String) e.g., "Finance", "Legal", "Personal", "HR"
            - "author": (String) Name of sender/author (or null)
            - "date": (String) Main date in document YYYY-MM-DD or YYYY (or null)
            - "language": (String) ISO code e.g., "de", "en"
            - "keywords": (List[String]) Top 5 relevant topics/tags
            - "entities": (List[String]) Key companies or people mentioned
            - "summary": (String) Concise summary of content
            
            Document Text:
            {text[:4000]}
            """
            response = llm.complete(prompt_str)
            
            # JSON extraction
            json_str = response.text
            match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {}
        except Exception as e:
            logger.error(f"Metadata extraction failed: {e}")
            return {"document_type": "Unknown", "error": str(e)}

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        """
        Generates an embedding vector for the given text.
        """
        try:
            # logger.info("Generating embedding...") # Verbose logging removed
            embed_model = RAGFactory.get_embedding_model()
            return embed_model.get_text_embedding(text)
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise e

    @classmethod
    def plan_query(cls, question: str) -> Dict[str, Any]:
        return {
            "original_question": question,
            "rewritten_question": question,
            "intent": "SEARCH",
            "filters": {}
        }

    @classmethod
    def reset_database(cls) -> Dict[str, str]:
        """
        Clears the Vector Database.
        """
        try:
            logger.info("Resetting Database...")
            client = RAGFactory.get_qdrant_client()
            collection_name = "securedoc_collection"
            
            client.delete_collection(collection_name=collection_name)
            
            # Recreate collection immediately
            from qdrant_client.http import models
            client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
            )
            
            logger.info(f"Collection {collection_name} cleared.")
            return {"status": "success", "message": f"Collection {collection_name} cleared."}
        except Exception as e:
            logger.error(f"Reset failed: {e}")
            raise e
