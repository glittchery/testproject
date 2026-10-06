import asyncio
from fastapi import FastAPI
from src.database.queries import create_tables
from src.database.models import Documents
from contextlib import asynccontextmanager
from src.services import create_index, insert_documents, search_documents, delete_document



@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables() #создаем таблицу
    await create_index() #создаем индекс
    await insert_documents() #добавляем данные из файла в таблицу и индекс
    yield


app = FastAPI(lifespan=lifespan)

@app.get("/search_elements/{text}")
async def search(text: str) -> list[Documents]:
    response = await search_documents(text)
    return response

@app.delete("/delete_element/{id}")
async def deletion(document_id: int):
    await delete_document(document_id)
    return {"success": True}

@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

