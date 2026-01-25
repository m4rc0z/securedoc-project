import sys
from unittest.mock import MagicMock

# -- MOCKING DEPENDENCIES START --
# Hack to bypass "llama-index-readers-docling" (requires Py3.10+) on Py3.9
mock_docling = MagicMock()
sys.modules["llama_index.readers.docling"] = mock_docling
# -- MOCKING DEPENDENCIES END --

import pytest
from unittest.mock import MagicMock, patch
from llama_index.core.schema import NodeWithScore, TextNode, QueryBundle
from app.rag.postprocessors import FlashRankRerank
from app.rag.retrieval import RetrievalService

class TestFlashRankRerank:
    """
    Tests the custom FlashRankRerank postprocessor.
    """
    
    @patch("app.rag.postprocessors.Ranker")
    def test_rerank_logic(self, mock_ranker_cls):
        """
        Verifies that _postprocess_nodes calls FlashRank and respects top_n.
        """
        # Setup Mock Ranker instance
        mock_ranker_instance = MagicMock()
        mock_ranker_cls.return_value = mock_ranker_instance
        
        # Mock Response from FlashRank: Return reversed order (id "1" is better than "0")
        # Input IDs will be "0", "1".
        # Let's say Node 1 is significantly more relevant.
        mock_ranker_instance.rank.return_value = [
            {"id": "1", "score": 0.99, "text": "World Content"},
            {"id": "0", "score": 0.10, "text": "Hello Content"}
        ]
        
        # Initialize Reranker
        reranker = FlashRankRerank(top_n=1) # Only keep top 1
        
        # Input Nodes
        node0 = NodeWithScore(node=TextNode(text="Hello Content"), score=0.5)
        node1 = NodeWithScore(node=TextNode(text="World Content"), score=0.5)
        nodes = [node0, node1]
        
        query = QueryBundle("query")
        
        # Execute
        new_nodes = reranker._postprocess_nodes(nodes, query)
        
        # Verify
        assert len(new_nodes) == 1
        assert new_nodes[0].get_content() == "World Content"
        assert new_nodes[0].score == 0.99

class TestRetrievalIntegration:
    """
    Verifies that RetrievalService is configured correctly.
    """
    
    @patch("app.rag.factory.RAGFactory.get_index")
    @patch("app.rag.factory.RAGFactory.get_llm")
    def test_get_query_engine_configuration(self, mock_get_llm, mock_get_index):
        """
        Verifies that as_chat_engine is called with node_postprocessors.
        """
        mock_index = MagicMock()
        mock_get_index.return_value = mock_index
        
        # Call the method
        RetrievalService.get_query_engine()
        
        # Check arguments passed to as_chat_engine
        mock_index.as_chat_engine.assert_called_once()
        _, kwargs = mock_index.as_chat_engine.call_args
        
        assert kwargs["similarity_top_k"] == 20
        assert "node_postprocessors" in kwargs
        assert len(kwargs["node_postprocessors"]) > 0
        assert isinstance(kwargs["node_postprocessors"][0], FlashRankRerank)
