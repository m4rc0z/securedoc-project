import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .config import settings
from .models import EmbedRequest, EmbedResponse, RAGRequest, RAGResponse
from .services import AIService
from .database import engine, Base, get_db
from .repositories import DocumentRepository

# --- Logging Setup ---
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ai_service")

# --- Lifespan Management (Startup/Shutdown) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load the AI models
    logger.info("Starting AI Service...")
    AIService.initialize()
    
    # Simple table creation for now (Dev mode)
    logger.info("Initializing Database...")
    async with engine.begin() as conn:
        # We need the vector extension for embeddings
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized.")
    
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

@app.post("/ingest", tags=["Database"])
async def ingest_document(text: str, source: str = "manual", db: AsyncSession = Depends(get_db)):
    """Convert text to vector and save it to Postgres."""
    try:
        vector = AIService.get_embedding(text)
        repo = DocumentRepository(db)
        await repo.create_vector_extension() # Just to be safe
        doc = await repo.save_chunk(source, text, vector)
        return {"status": "saved", "id": doc.id}
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", tags=["Database"])
async def search_documents(query: str, db: AsyncSession = Depends(get_db)):
    """Find similar documents using vector search."""
    try:
        vector = AIService.get_embedding(query)
        repo = DocumentRepository(db)
        results = await repo.search_similar(vector)
        return {"matches": [{"content": r.content, "source": r.source_file} for r in results]}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask", response_model=RAGResponse, tags=["AI Capabilities"])
def ask_llm(request: RAGRequest):
    try:
        answer = AIService.ask_llm(request.question, request.context)
        return RAGResponse(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LLM service unavailable")
