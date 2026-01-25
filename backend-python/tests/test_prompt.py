import sys
from unittest.mock import MagicMock

# -- MOCKING DEPENDENCIES START --
# Hack to bypass "llama-index-readers-docling" (requires Py3.10+) on Py3.9
mock_docling = MagicMock()
sys.modules["llama_index.readers.docling"] = mock_docling
# -- MOCKING DEPENDENCIES END --

import pytest
from unittest.mock import patch
# Now we can import app.services because the failing import inside it is mocked
from app.services import AIService
from app.prompts.manager import PromptManager

class TestPromptManager:
    """
    Tests for the PromptManager class and Jinja2 rendering.
    """
    def test_get_chat_prompt_rendering(self):
        """
        Verifies that the chat prompt is rendered correctly with chunks and question.
        """
        chunks = ["Chunk 1 content", "Chunk 2 content"]
        question = "What is the content?"
        date_str = "2023-01-01"
        
        prompt = PromptManager.get_chat_prompt(chunks, question, date_str)
        
        assert "Chunk 1 content" in prompt
        assert "Chunk 2 content" in prompt
        assert "What is the content?" in prompt
        assert "2023-01-01" in prompt
        assert "Reference Date:" in prompt
        assert "Guideline:" in prompt

    def test_get_chat_prompt_no_date(self):
        """
        Verifies that it defaults to today's date if none provided.
        """
        chunks = ["A"]
        question = "Q"
        prompt = PromptManager.get_chat_prompt(chunks, question)
        assert "Reference Date:" in prompt


class TestAIServicePrompting:
    """
    Tests integration of AIService with PromptManager.
    """

    @pytest.mark.asyncio
    @patch('app.services.AIService._llm', create=True) 
    @patch('app.services.RAGFactory.get_llm')
    @patch('app.services.PromptManager.get_chat_prompt')
    async def test_ask_llm_uses_prompt_manager(self, mock_get_prompt, mock_get_llm, mock_llm_prop):
        """
        Verifies that AIService.ask_llm calls PromptManager when context is present.
        """
        # Setup Mocks
        mock_llm_instance = MagicMock()
        mock_llm_instance.complete.return_value.text = "Mock Answer"
        mock_get_llm.return_value = mock_llm_instance
        
        mock_get_prompt.return_value = "Rendered Prompt"
        
        # Test Input
        question = "Question?"
        context = "Chunk1\n---\nChunk2"
        
        # Action
        result = await AIService.ask_llm(question, context)
        
        # Verify
        mock_get_prompt.assert_called_once()
        args, _ = mock_get_prompt.call_args
        # AIService splits by "\n---\n"
        chunks_arg = args[0]
        assert chunks_arg == ["Chunk1", "Chunk2"]
        assert args[1] == question
        
        mock_llm_instance.complete.assert_called_with("Rendered Prompt")
        assert result["answer"] == "Mock Answer"
