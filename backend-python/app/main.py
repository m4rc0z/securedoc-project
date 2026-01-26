import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from .config import settings
# Facade Import (Simpler)
from . import EmbedRequest, EmbedResponse, RAGRequest, RAGResponse, IngestRequest, IngestResponse, RerankRequest, RerankResponse, PlanRequest, PlanResponse, AIService

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



@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    import traceback
    logger.error(f"Global Exception: {exc}\n{traceback.format_exc()}")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal Server Error from Global Handler"},
    )

from fastapi.responses import JSONResponse

@app.post("/embed", response_model=EmbedResponse, tags=["AI Capabilities"])
def create_embedding(request: EmbedRequest):
    # CPU-bound operation: defined as sync 'def' so FastAPI runs it in a separate threadpool.
    # If this were 'async def', it would block the main event loop during calculation.
    try:
        logger.info(f"Embed request for text: {request.text[:50]}...")
        vector = AIService.get_embedding(request.text)
        logger.info(f"Vector generated: {type(vector)}, Len: {len(vector) if vector else 'None'}")
        return EmbedResponse(embedding=vector)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal processing error")

@app.post("/ingest", response_model=IngestResponse, tags=["AI Capabilities"])
async def ingest_document(request: IngestRequest):
    try:
        # Metadata extraction
        extracted_meta = await AIService.extract_metadata(request.text)
        
        # Merge with request metadata, prioritizing request-provided values
        final_doc_metadata = {**extracted_meta, **request.metadata}
        
        # Embed and store chunks
        chunks = AIService.process_document(request.text, final_doc_metadata)
        
        return IngestResponse(document_metadata=final_doc_metadata, chunks=chunks)
    except Exception as e:
        logger.error(f"Ingest failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@app.post("/ask", response_model=RAGResponse, tags=["AI Capabilities"])
async def ask_llm(request: RAGRequest):
    try:
        response_data = await AIService.ask_llm(request.question, request.context)
        
        # Handle both dict (new) and string (legacy/fallback) returns
        if isinstance(response_data, dict):
            return RAGResponse(answer=response_data["answer"], sources=response_data.get("sources", []))
        else:
            return RAGResponse(answer=str(response_data), sources=[])
    except Exception as e:
        logger.error(f"Ask LLM failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/rerank", response_model=RerankResponse, tags=["AI Capabilities"])
def rerank_documents(request: RerankRequest):
    try:
        results = AIService.rerank(request.query, request.documents, request.top_k)
        return RerankResponse(results=results)
    except Exception as e:
        logger.error(f"Rerank failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@app.post("/plan", response_model=PlanResponse, tags=["AI Capabilities"])
def plan_query_endpoint(request: PlanRequest):
    try:
        plan = AIService.plan_query(request.question)
        return PlanResponse(
            original_question=plan.get("original_question", ""),
            rewritten_question=plan.get("rewritten_question", ""),
            intent=plan.get("intent", "SEARCH"),
            filters=plan.get("filters", {})
        )
    except Exception as e:
        logger.error(f"Plan query failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
@app.post("/reset", tags=["System"])
def reset_system():
    try:
        result = AIService.reset_database()
        return result
    except Exception as e:
        logger.error(f"System reset failed: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
