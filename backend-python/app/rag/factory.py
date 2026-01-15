import logging
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.storage.storage_context import StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, AsyncQdrantClient
import torch

from ..config import settings

logger = logging.getLogger("rag_factory")

class RAGFactory:
    _llm = None
    _embed_model = None
    _qdrant_client = None
    _aclient = None
    _vector_store = None
    _index = None

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

    @classmethod
    def get_qdrant_client(cls):
        if not cls._qdrant_client:
            url = "http://qdrant:6333" 
            logger.info(f"Connecting to Qdrant at {url}")
            cls._qdrant_client = QdrantClient(url=url)
            cls._aclient = AsyncQdrantClient(url=url)
        return cls._qdrant_client

    @classmethod
    def get_vector_store(cls):
        if not cls._vector_store:
            client = cls.get_qdrant_client()
            cls._vector_store = QdrantVectorStore(
                client=client,
                aclient=cls._aclient,
                collection_name="securedoc_collection",
                enable_hybrid=False, # Revert to Dense
                batch_size=20
            )
        return cls._vector_store
    
    @classmethod
    def get_index(cls):
        """
        Returns the VectorStoreIndex. 
        Note: Use from_vector_store to load existing, or creating new if empty.
        Here we generally want to load the index wrapper around the store.
        """
        vector_store = cls.get_vector_store()
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # We don't build from documents here, just load the index interface
        cls._index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context,
            embed_model=cls.get_embedding_model()
        )
        return cls._index
