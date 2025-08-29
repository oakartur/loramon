import os
import logging
from urllib.parse import urlparse
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("DATABASE_URLS", "")

# garantir driver async
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

host = urlparse(DATABASE_URL).hostname
logger.info("Connecting to database at %s", host)

engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
)

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()
