import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from .config import settings
# Facade Import (Simpler)
from . import EmbedRequest, EmbedResponse, RAGRequest, RAGResponse, IngestRequest, IngestResponse, RerankRequest, RerankResponse, AIService

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ai_service")

# Handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models when app starts
    logger.info("Starting AI Service...")
    AIService.initialize()
    
    yield
    
    # Cleanup on exit
    logger.info("Shutting down AI Service...")

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

@app.post("/ingest", response_model=IngestResponse, tags=["AI Capabilities"])
def ingest_document(request: IngestRequest):
    try:
        chunks = AIService.process_document(request.text, request.metadata)
        return IngestResponse(chunks=chunks)
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/ask", response_model=RAGResponse, tags=["AI Capabilities"])
def ask_llm(request: RAGRequest):
    try:
        answer = AIService.ask_llm(request.question, request.context)
        return RAGResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM service unavailable")

@app.post("/rerank", response_model=RerankResponse, tags=["AI Capabilities"])
def rerank_documents(request: RerankRequest):
    try:
        results = AIService.rerank(request.query, request.documents, request.top_k)
        return RerankResponse(results=results)
    except Exception as e:
        logger.error(f"Rerank failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
