import logging
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import torch

from ..config import settings

logger = logging.getLogger("rag_factory")

class RAGFactory:
    _llm = None
    _embed_model = None
    _llm = None
    _embed_model = None

    @classmethod
    def get_llm(cls):
        if not cls._llm:
            logger.info(f"Initializing Ollama LLM: {settings.ollama_model} at {settings.ollama_base_url}")
            cls._llm = Ollama(
                model=settings.ollama_model,
                base_url=settings.ollama_base_url,
                request_timeout=600.0,
                temperature=0.1,
                context_window=8192,
                additional_kwargs={"num_ctx": 8192}
            )
            Settings.llm = cls._llm
        return cls._llm

    @classmethod
    def get_embedding_model(cls):
        if not cls._embed_model:
            logger.info(f"Initializing Embedding Model: {settings.embedding_model_name}")
            # Check device availability (MPS for Mac M-series, but Docker Linux uses CPU)
            device = "mps" if torch.backends.mps.is_available() else "cpu"
            logger.info(f"Using device: {device}")
            
            cls._embed_model = HuggingFaceEmbedding(
                model_name=settings.embedding_model_name,
                device=device
            )
            Settings.embed_model = cls._embed_model
        return cls._embed_model

