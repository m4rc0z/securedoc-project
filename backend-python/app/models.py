from typing import List
from pydantic import BaseModel, Field

class EmbedRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text to verify")

class EmbedResponse(BaseModel):
    embedding: List[float]

class RAGRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: str = Field(default="", description="Retrieved context or empty string")

class RAGResponse(BaseModel):
    answer: str
    sources: List[str] = []

class IngestRequest(BaseModel):
    text: str
    metadata: dict = {}

class ChunkData(BaseModel):
    content: str
    embedding: List[float]
    metadata: dict = {}

class IngestResponse(BaseModel):
    document_metadata: dict = {}
    chunks: List[ChunkData]

class RerankRequest(BaseModel):
    query: str = Field(..., min_length=1)
    documents: List[str] = Field(..., min_length=1)
    top_k: int = 5

class ScoredDocument(BaseModel):
    content: str
    score: float

class RerankResponse(BaseModel):
    results: List[ScoredDocument]

class PlanRequest(BaseModel):
    question: str = Field(..., min_length=1)

class PlanResponse(BaseModel):
    original_question: str
    rewritten_question: str
    intent: str
    filters: dict = {}
