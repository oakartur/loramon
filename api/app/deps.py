from .database import SessionLocal

# Dependency do FastAPI: entrega uma AsyncSession válida
async def get_db():
    async with SessionLocal() as session:
        yield session
