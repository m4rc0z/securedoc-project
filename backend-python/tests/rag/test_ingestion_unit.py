import pytest
from unittest.mock import MagicMock, patch
import sys

# MOCK MISSING DEPENDENCIES FOR LOCAL TESTING (Python 3.9 vs 3.11 issue)
sys.modules["llama_index.readers.docling"] = MagicMock()
sys.modules["llama_index.readers.docling"].DoclingReader = MagicMock()

from app.rag.factory import RAGFactory
from app.rag.ingestion import IngestionService

@pytest.fixture
def mock_settings():
    with patch("app.rag.factory.settings") as mock:
        mock.ollama_base_url = "http://mock-ollama:11434"
        mock.ollama_model = "llama3-mock"
        mock.embedding_model_name = "mock-embed"
        yield mock

@patch("app.rag.factory.Settings")
def test_factory_get_llm(MockSettings, mock_settings):
    # Reset singleton
    RAGFactory._llm = None
    with patch("app.rag.factory.Ollama") as MockOllama:
        llm = RAGFactory.get_llm()
        assert llm is not None
        MockOllama.assert_called_once()
        # Ensure Settings.llm was set
        assert MockSettings.llm == llm

@patch("app.rag.factory.Settings")
def test_factory_get_embedding(MockSettings, mock_settings):
    # Reset singleton
    RAGFactory._embed_model = None
    with patch("app.rag.factory.HuggingFaceEmbedding") as MockEmbed:
        embed = RAGFactory.get_embedding_model()
        assert embed is not None
        MockEmbed.assert_called_once()
        # Ensure Settings.embed_model was set
        assert MockSettings.embed_model == embed

@patch("app.rag.ingestion.DoclingReader")
@patch("app.rag.ingestion.RAGFactory")
@patch("app.rag.ingestion.IngestionPipeline")
@patch("app.rag.ingestion.SemanticSplitterNodeParser")
def test_ingestion_process_file(MockSplitter, MockPipeline, MockFactory, MockReader):
    # Setup Mocks
    mock_reader_instance = MockReader.return_value
    mock_doc = MagicMock()
    mock_doc.metadata = {}
    mock_reader_instance.load_data.return_value = [mock_doc]
    
    mock_pipeline_instance = MockPipeline.return_value
    mock_pipeline_instance.run.return_value = [MagicMock(), MagicMock()] # Returns 2 nodes

    # Execution
    nodes = IngestionService.process_file("dummy.pdf", {"filename": "dummy.pdf"})

    # Assertions
    MockReader.assert_called()
    assert len(nodes) == 2
    assert mock_doc.metadata["filename"] == "dummy.pdf"
