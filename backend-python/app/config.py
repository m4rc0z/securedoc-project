from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "SecureDoc AI Service"
    embedding_model_name: str = "all-MiniLM-L6-v2"
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", env="OLLAMA_BASE_URL")
    ollama_model: str = "llama3.1:latest"
    log_level: str = "INFO"
    database_url: str = Field(default="postgresql://admin:secretpassword@localhost:5432/securedoc", env="DATABASE_URL")

    model_config = {
        "env_file": ".env",
        "protected_namespaces": ("settings_",)
    }

settings = Settings()
