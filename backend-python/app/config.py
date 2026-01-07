from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "SecureDoc AI Service"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    ollama_base_url: str = Field(default="http://host.docker.internal:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = "tinyllama"
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "protected_namespaces": ("settings_",)
    }

settings = Settings()
