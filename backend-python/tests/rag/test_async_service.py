import pytest
import asyncio
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import sys

# MOCK DOCLING
sys.modules["llama_index.readers.docling"] = MagicMock()
sys.modules["llama_index.readers.docling"].DoclingReader = MagicMock()

from app.services import AIService

@pytest.mark.asyncio
@patch("app.services.RetrievalService")
async def test_ask_llm_async_success(MockRetrieval):
    # Setup
    mock_engine = MagicMock()
    # verify aquery is called and awaits
    future = asyncio.Future()
    future.set_result(MagicMock(source_nodes=[], __str__=lambda x: "Answer"))
    mock_engine.aquery.return_value = future
    
    MockRetrieval.get_query_engine.return_value = mock_engine
    
    # Act
    response = await AIService.ask_llm("question")
    
    # Assert
    assert response["answer"] == "Answer"
    mock_engine.aquery.assert_called_once()

@pytest.mark.asyncio
@patch("app.services.RetrievalService")
async def test_ask_llm_timeout(MockRetrieval):
    # Setup
    mock_engine = MagicMock()
    
    async def slow_query(*args, **kwargs):
        await asyncio.sleep(3.0) # Longer than 2s timeout
        return "Should not reach here"
        
    mock_engine.aquery.side_effect = slow_query
    MockRetrieval.get_query_engine.return_value = mock_engine
    
    # Act
    response = await AIService.ask_llm("question")
    
    # Assert
    assert "couldn't search the documents fast enough" in response["answer"]
    assert "System: Timeout" in response["sources"]
