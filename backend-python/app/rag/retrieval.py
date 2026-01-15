import logging
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import MetadataReplacementPostProcessor
from llama_index.core.schema import  QueryBundle
from llama_index.core.base.base_query_engine import BaseQueryEngine
from llama_index.core.base.response.schema import Response
from .factory import RAGFactory

logger = logging.getLogger("rag_retrieval")

class RetrievalService:
    @staticmethod
    def get_query_engine():
        """
        Configures the RAG Retrieval Engine using Hybrid Search components.
        """
        index = RAGFactory.get_index()
        
        # Retrieval Configuration (Dense Search)
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=8,
            vector_store_query_mode="default",
        )

        
        # Chat Engine Configuration
        # Uses a unified agent for context-aware generation.
        agent = index.as_chat_engine(
            chat_mode="context",
            llm=RAGFactory.get_llm(),
            verbose=True,
            similarity_top_k=8,
            vector_store_query_mode="default",
            system_prompt=(
                "You are a helpful and precise assistant. "
                "Context information is below.\n"
                "---------------------\n"
                "{context_str}\n"
                "---------------------\n"
                "Guideline: Provide a DETAILED and COMPREHENSIVE answer based on the context.\n"
                "1. Specificity: Include relevant details and specific evidence. Avoid generic summaries.\n"
                "2. Relevance: Include dates or metrics ONLY if they explicitly answer the question.\n"
                "3. Calculation: If a timeline/duration is requested, calculate it explicitly.\n"
                "4. Language: Answer in the same language as the question."
            )
        )
        
        return agent
