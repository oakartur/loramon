import logging
from .database import SessionLocal

logger = logging.getLogger(__name__)

# Dependency do FastAPI: entrega uma AsyncSession válida
async def get_db():
    logger.info("Opening database session")
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            logger.info("Closing database session")
