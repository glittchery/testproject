import asyncio
from fastapi import FastAPI
from src.database.queries import create_tables
from contextlib import asynccontextmanager
from pydantic import BaseModel
from datetime import datetime
class DocumentSchema(BaseModel):
    id: int
    rubrics: list[str]
    text: str
    created_date: datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/search_text")
async def search(text: str) -> list[DocumentSchema]:
    ...




@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}