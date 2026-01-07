import logging
from typing import List, Optional, Dict
from langchain_community.llms import Ollama
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from tenacity import retry, stop_after_attempt, wait_exponential
from sentence_transformers import SentenceTransformer, CrossEncoder

from .config import settings

logger = logging.getLogger("ai_service")

class AIService:
    _embedding_model: Optional[SentenceTransformer] = None
    _rerank_model: Optional[CrossEncoder] = None
    _llm: Optional[Ollama] = None

    @classmethod
    def initialize(cls):
        """Init embedding model and LLM connection."""
        logger.info(f"Loading embedding model: {settings.embedding_model_name}...")
        try:
            cls._embedding_model = SentenceTransformer(settings.embedding_model_name)
            # Use a lightweight CrossEncoder for re-ranking
            cls._rerank_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2') 
            logger.info("Embedding and Re-ranking models loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load AI models: {e}")
            raise e

        logger.info(f"Initializing Ollama connection to {settings.ollama_base_url}...")
        cls._llm = Ollama(base_url=settings.ollama_base_url, model=settings.ollama_model)

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        if not cls._embedding_model:
            raise RuntimeError("Embedding model is not initialized")
        
        try:
            if not text.strip():
                raise ValueError("Input text cannot be empty")
            
            prediction = cls._embedding_model.encode(text)
            return prediction.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise e

    @classmethod
    def process_document(cls, text: str, metadata: dict = {}) -> List[dict]:
        """
        Splits text into chunks and generates embeddings.
        Splits text into chunks, generates embeddings for each chunk, and combines with metadata.
        Returns a list of dictionaries, each containing 'content', 'embedding', and 'metadata'.
        """
        if not cls._embedding_model:
            raise RuntimeError("Embedding model is not initialized")

        try:
            # 1. Split Text
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                is_separator_regex=False,
            )
            
            # Create documents with metadata
            chunks = text_splitter.create_documents([text], metadatas=[metadata])
            
            logger.info(f"Split document into {len(chunks)} chunks.")

            results = []
            # 2. Embed each chunk
            for chunk in chunks:
                vector = cls.get_embedding(chunk.page_content)
                results.append({
                    "content": chunk.page_content,
                    "embedding": vector,
                    "metadata": chunk.metadata
                })
            
            return results

        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            raise e

    @classmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def ask_llm(cls, question: str, context: str) -> str:
        if not cls._llm:
            raise RuntimeError("LLM is not initialized")

        try:
            template = """
            You are a helpful assistant for analyzing documents.
            Answer the question based ONLY on the following context:
            {context}
            
            Question: {question}
            
            If the answer is not in the context, say "I cannot answer this based on the provided document."
            """
            prompt = PromptTemplate.from_template(template)
            chain = prompt | cls._llm
            
            logger.debug(f"Sending request to LLM. Question: {question}")
            result = chain.invoke({"context": context, "question": question})
            return result
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            raise e

    @classmethod
    def rerank(cls, query: str, documents: List[str], top_k: int = 5) -> List[Dict]:
        """
        Re-ranks a list of documents based on their relevance to the query using a CrossEncoder.
        Returns the top_k sorted documents with scores.
        """
        if not cls._rerank_model:
             # Lazy load if not initialized or raise error
             raise RuntimeError("Rerank model is not initialized")

        if not documents:
            return []

        # Create pairs [query, doc]
        pairs = [[query, doc] for doc in documents]
        
        # CrossEncoder predicts a score (higher is better)
        scores = cls._rerank_model.predict(pairs)
        
        # Combine docs with scores
        doc_scores = [{"content": doc, "score": float(score)} for doc, score in zip(documents, scores)]
        
        # Sort descending
        doc_scores.sort(key=lambda x: x["score"], reverse=True)
        
        return doc_scores[:top_k]
