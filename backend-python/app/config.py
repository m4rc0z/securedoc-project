from pydantic import Field
from pydantic_settings import BaseSettings

# --- App Config (Loaded from .env) ---
class Settings(BaseSettings):
    app_name: str = "SecureDoc AI Service"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    database_url: str = Field(default="postgresql+asyncpg://admin:secretpassword@db:5432/securedoc", env="DATABASE_URL")
    ollama_base_url: str = Field(default="http://host.docker.internal:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = "llama3"
    log_level: str = "INFO"

    model_config = {
        "env_file": ".env",
        "protected_namespaces": ("settings_",)
    }

settings = Settings()
