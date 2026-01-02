import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from .config import settings
from .models import EmbedRequest, EmbedResponse, RAGRequest, RAGResponse
from .services import AIService

# --- Logging Setup ---
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ai_service")

# --- Lifespan Management (Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AI Service...")
    AIService.initialize()
    yield
    # Shutdown
    logger.info("Shutting down AI Service...")

# --- Main Application ---
app = FastAPI(
    title=settings.app_name,
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "config": {"model": settings.embedding_model_name, "ollama": settings.ollama_base_url}}

@app.post("/embed", response_model=EmbedResponse, tags=["AI Capabilities"])
def create_embedding(request: EmbedRequest):
    try:
        vector = AIService.get_embedding(request.text)
        return EmbedResponse(embedding=vector)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal processing error")

@app.post("/ask", response_model=RAGResponse, tags=["AI Capabilities"])
def ask_llm(request: RAGRequest):
    try:
        answer = AIService.ask_llm(request.question, request.context)
        return RAGResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM service unavailable")
