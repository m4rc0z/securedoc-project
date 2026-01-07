from typing import List
from pydantic import BaseModel, Field

class EmbedRequest(BaseModel):
    text: str = Field(..., min_length=1, description="The text to verify")

class EmbedResponse(BaseModel):
    embedding: List[float]

class RAGRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: str = Field(..., min_length=1)

class RAGResponse(BaseModel):
    answer: str

class IngestRequest(BaseModel):
    text: str
    metadata: dict = {}

class ChunkData(BaseModel):
    content: str
    embedding: List[float]
    metadata: dict = {}

class IngestResponse(BaseModel):
    chunks: List[ChunkData]
