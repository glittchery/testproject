from fastapi import FastAPI, Query, Path
from src.database.queries import create_tables
from datetime import datetime
from contextlib import asynccontextmanager
from src.services import create_index, insert_documents, search_documents, delete_document, es_client_close
from pydantic import BaseModel, ConfigDict

class DocumentSchema(BaseModel):
    id: int
    text: str
    rubrics: list[str]
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables() #создаем таблицу
    await create_index() #создаем индекс
    await insert_documents() #добавляем данные из файла в таблицу и индекс
    yield
    await es_client_close()

tags_metadata = [
    {
        "name": "Documents",
        "description": "Search and delete documents.",
    },
]

app = FastAPI(
    lifespan=lifespan,
    title="Document Search API",
    description="API for searching documents using Elasticsearch.",
    openapi_tags=tags_metadata,
)

@app.get(
    "/search",
    response_model=list[DocumentSchema],
    tags=["Documents"],
    summary="Search documents",
    description="Search documents by text. Returns up to 20 documents sorted by creation date.",
)
async def search(
        query: str = Query(
            min_length=1,
            description="Text to search for.",
            examples=["example"],
        )
):
    response = await search_documents(query)
    return response

@app.delete(
    "/documents/{document_id}",
    status_code=204,
    tags=["Documents"],
    summary="Delete document",
    description="Delete a document from the database and Elasticsearch by id(int32).",
    responses={
        204: {"description": "Document deleted successfully"},
        404: {"description": "Document not found"},
    },
)
async def deletion(
        document_id: int = Path(
            gt=0,
            le=2147483647,
            description="Document id(int32).",
            examples=[1]
        )
):
    response = await delete_document(document_id)
    return response


@app.get("/health", include_in_schema=False)
async def health():
    return {"status": "ok"}

