import logging
from typing import List, Optional, Dict, Any
import re
import json
import asyncio


from tenacity import retry, stop_after_attempt, wait_exponential

from .config import settings
from .rag.factory import RAGFactory
from .rag.ingestion import IngestionService
from llama_index.core.schema import NodeWithScore, TextNode
from .prompts.manager import PromptManager

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
        # RAGFactory.get_index() removed (Retrieval is handled by Java)
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
                
                # Add current date for relative time understanding
                import datetime
                today_str = datetime.date.today().strftime("%Y-%m-%d")
                
                # Reconstruct chunks list for the PromptManager
                chunks = context.split("\n---\n")
                prompt = PromptManager.get_chat_prompt(chunks, question, today_str)
                response = llm.complete(prompt)
                response_text = response.text
                
                return {
                    "answer": response_text,
                    "sources": ["Provided Context"]
                }

            # Fallback for no context: Just warn the user that context is required
            return {
                "answer": "I can only answer questions based on selected documents. Please ensure the system has retrieved relevant documents.",
                "sources": []
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
    async def extract_metadata(cls, text: str) -> dict:
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
            
            # Async extraction with timeout
            import asyncio
            response = await asyncio.wait_for(llm.acomplete(prompt_str), timeout=30.0)
            
            # JSON extraction
            json_str = response.text
            match = re.search(r'\{.*\}', json_str, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return {}
        except asyncio.TimeoutError:
            logger.error("Metadata extraction timed out.")
            return {"document_type": "Unknown", "error": "Timeout"}
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
        """
        [PLACEHOLDER] Future Reasoning Engine
        
        This method uses an LLM to analyze the question before searching.
        
        It performs two main tasks:
        1. Query Decomposition: Breaks complex questions into smaller parts.
           (Example: "Compare 2022 and 2023" -> "Search 2022", "Search 2023")
        2. Query Rewriting: Clarifies the question for better search results.
           (Example: "How do I install it?" -> "Installation instructions for Docker")
        """
        return {
            "original_question": question,
            "rewritten_question": question,
            "intent": "SEARCH",
            "filters": {}
        }

    @classmethod
    async def reset_database(cls):
        """
        Resets the database. 
        In this architecture, vector data is managed by Postgres (Java).
        """
        logger.info("Reset database request received. (Handled by Postgres/Java)")
        return {"status": "success", "message": "Database reset not supported in Python service."}
