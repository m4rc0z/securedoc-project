import os
import logging
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import date

logger = logging.getLogger("ai_service")

class PromptManager:
    _env = None

    @classmethod
    def _get_env(cls) -> Environment:
        if cls._env is None:
            # Assumes this file is in backend-python/app/prompts/manager.py
            # Templates are in backend-python/app/prompts/templates
            current_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(current_dir, "templates")
            
            logger.info(f"Loading prompt templates from: {templates_dir}")
            
            cls._env = Environment(
                loader=FileSystemLoader(templates_dir),
                autoescape=select_autoescape(['html', 'xml', 'j2'])
            )
        return cls._env

    @classmethod
    def get_chat_prompt(cls, chunks: List[str], question: str, reference_date: str = None) -> str:
        """
        Renders the chat prompt using the 'chat_prompt.j2' template.
        """
        if reference_date is None:
            reference_date = date.today().strftime("%Y-%m-%d")

        try:
            env = cls._get_env()
            template = env.get_template("chat_prompt.j2")
            
            return template.render(
                chunks=chunks,
                question=question,
                reference_date=reference_date
            )
        except Exception as e:
            logger.error(f"Failed to render chat prompt: {e}")
            # Fallback to a safe default or re-raise depending on strategy. 
            # Re-raising ensures we catch config errors early.
            raise e
