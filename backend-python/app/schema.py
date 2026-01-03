from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from .database import Base

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)
    source_file = Column(String, index=True)  # Filename to filter by document
    content = Column(Text)                    # The actual text chunk
    embedding = Column(Vector(384))           # Embeddings (MiniLM has 384 dims)
