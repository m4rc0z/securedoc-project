from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from .config import settings

# 1. Setup the DB Connection (Async)
engine = create_async_engine(
    settings.database_url,
    echo=(settings.log_level == "DEBUG"), # See SQL queries when developing
    future=True
)

# 2. Session Factory (creates new DB sessions)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 3. Base class for our DB Models
Base = declarative_base()

# 4. Dependency for FastAPI (get_db)
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
