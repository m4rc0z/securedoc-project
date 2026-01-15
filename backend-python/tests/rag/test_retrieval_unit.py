import pytest
from unittest.mock import MagicMock, patch
import sys

# sys.modules hacks removed as libraries are installed


from app.rag.retrieval import RetrievalService
from llama_index.core.schema import NodeWithScore, TextNode

@patch("app.rag.retrieval.RAGFactory")
@patch("app.rag.retrieval.VectorIndexRetriever")
@patch("app.rag.retrieval.SubQuestionQueryEngine")
@patch("app.rag.factory.Settings") # Patch settings again to avoid validation
def test_get_query_engine(MockSettings, MockSubQuery, MockRetriever, MockFactory):
    # Setup
    MockFactory.get_index.return_value = MagicMock()
    MockFactory.get_llm.return_value = MagicMock()
    
    # Act
    engine = RetrievalService.get_query_engine()
    
    # Assert
    MockFactory.get_index.assert_called_once()
    MockRetriever.assert_called_once()
    # Check hybrid mode
    args, kwargs = MockRetriever.call_args
    assert kwargs.get("vector_store_query_mode") == "hybrid"
    assert kwargs.get("similarity_top_k") == 50
    
    MockSubQuery.from_defaults.assert_called()

def test_flashrank_logic():
    # Unit test for the mapping logic inside our custom class
    # We need to mock the Ranker class where it is imported in retrieval.py
    with patch("app.rag.retrieval.Ranker") as MockRanker:
        from app.rag.retrieval import FlashRankRerank # Local import to avoid import errors at top level if not careful
        reranker = FlashRankRerank()
        ranker_instance = MockRanker.return_value
        ranker_instance.rerank.return_value = [{"id": "1", "score": 0.9}]
        
        node = NodeWithScore(node=TextNode(id_="1", text="test"), score=0.5)
        
        results = reranker.rank("query", [node])
        
        ranker_instance.rerank.assert_called()
        assert len(results) == 1
        assert results[0].score == 0.9
