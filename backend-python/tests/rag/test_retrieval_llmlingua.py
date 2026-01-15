import pytest
from unittest.mock import MagicMock, patch
import sys

# MOCK DOCLING
sys.modules["llama_index.readers.docling"] = MagicMock()
sys.modules["llama_index.readers.docling"].DoclingReader = MagicMock()

from app.rag.retrieval import RetrievalService

@patch("app.rag.retrieval.RAGFactory")
@patch("app.rag.retrieval.VectorIndexRetriever")
@patch("app.rag.retrieval.get_response_synthesizer")
@patch("app.rag.retrieval.RetrieverQueryEngine")
@patch("app.rag.retrieval.SubQuestionQueryEngine")
def test_llmlingua_integration(MockSubQuestion, MockRetrieverEngine, MockSynthesizer, MockRetriever, MockFactory):
    # Act
    RetrievalService.get_query_engine()
    
    # Assert
    # Check if RetrieverQueryEngine was initialized with postprocessors
    args, kwargs = MockRetrieverEngine.call_args
    assert "node_postprocessors" in kwargs
    postprocessors = kwargs["node_postprocessors"]
    
    # We expect 2 postprocessors: FlashRank and LLMLingua
    assert len(postprocessors) == 2
    
    # Check basics (class names or attributes)
    has_flashrank = any("FlashRank" in str(type(p)) or "FlashRank" in str(p) or "FlashRank" in p.__class__.__name__ for p in postprocessors)
    has_llmlingua = any("LLMLingua" in str(type(p)) or "LLMLingua" in str(p) or "LLMLingua" in p.__class__.__name__ for p in postprocessors)
    
    assert has_flashrank, "FlashRank postprocessor missing"
    assert has_llmlingua, "LLMLingua postprocessor missing"
