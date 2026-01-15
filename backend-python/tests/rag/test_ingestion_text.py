import pytest
from unittest.mock import MagicMock, patch
import sys

# MOCK DOCLING FOR LOCAL TESTING (Python 3.9 issue)
sys.modules["llama_index.readers.docling"] = MagicMock()
sys.modules["llama_index.readers.docling"].DoclingReader = MagicMock()

# MOCK for tests
from app.rag.factory import RAGFactory
from app.rag.ingestion import IngestionService
from llama_index.core.schema import Document

@patch("app.rag.ingestion.RAGFactory")
@patch("app.rag.ingestion.IngestionPipeline")
@patch("app.rag.ingestion.SemanticSplitterNodeParser")
@patch("app.rag.factory.Settings") 
def test_process_text(MockSettings, MockSplitter, MockPipeline, MockFactory):
    # Setup
    mock_pipeline_instance = MockPipeline.return_value
    mock_pipeline_instance.run.return_value = [MagicMock(), MagicMock()] # Return 2 nodes
    
    # Act
    nodes = IngestionService.process_text("Some text", {"key": "value"})
    
    # Assert
    MockFactory.get_vector_store.assert_called()
    MockPipeline.assert_called()
    assert len(nodes) == 2
    
    # Verify pipeline was run with correct doc
    args, kwargs = mock_pipeline_instance.run.call_args
    assert "documents" in kwargs
    assert len(kwargs["documents"]) == 1
    assert kwargs["documents"][0].text == "Some text"
    assert kwargs["documents"][0].metadata["key"] == "value"
