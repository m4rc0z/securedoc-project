from typing import List, Tuple
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from .schema import DocumentChunk

class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_vector_extension(self):
        """Prepare the DB for vector operations."""
        await self.session.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await self.session.commit()

    async def save_chunk(self, source_file: str, content: str, embedding: List[float]) -> DocumentChunk:
        chunk = DocumentChunk(
            source_file=source_file,
            content=content,
            embedding=embedding
        )
        self.session.add(chunk)
        await self.session.commit()
        await self.session.refresh(chunk)
        return chunk

    async def search_similar(self, query_embedding: List[float], limit: int = 5) -> List[Tuple[DocumentChunk, float]]:
        # Find the closest matching vectors using L2 distance (Euclidean)
        stmt = select(DocumentChunk).order_by(
            DocumentChunk.embedding.l2_distance(query_embedding)
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        chunks = result.scalars().all()
        # Returns the list of matching chunks
        return chunks
