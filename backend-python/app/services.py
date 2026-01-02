import logging
from typing import List, Optional
from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate

from .config import settings

logger = logging.getLogger("ai_service")

class AIService:
    _embedding_model: Optional[SentenceTransformer] = None
    _llm: Optional[Ollama] = None

    @classmethod
    def initialize(cls):
        """Load heavy models on startup"""
        logger.info(f"Loading embedding model: {settings.embedding_model_name}...")
        try:
            cls._embedding_model = SentenceTransformer(settings.embedding_model_name)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise e

        logger.info(f"Initializing Ollama connection to {settings.ollama_base_url}...")
        cls._llm = Ollama(base_url=settings.ollama_base_url, model=settings.ollama_model)

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        if not cls._embedding_model:
            raise RuntimeError("Embedding model is not initialized")
        
        try:
            # Check for empty input to fail fast
            if not text.strip():
                raise ValueError("Input text cannot be empty")
                
            prediction = cls._embedding_model.encode(text)
            return prediction.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise e

    @classmethod
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
