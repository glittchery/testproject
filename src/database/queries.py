from src.database.database import engine, Base, session_factory
from src.database.models import Documents
from sqlalchemy import delete
from datetime import datetime

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# add element
# get element
# delete element

async def insert_document(rubrics: list[str], text:str, created_date: datetime):
    async with session_factory() as session:
        new_document = Documents(rubrics=rubrics, text=text, created_date=created_date)
        session.add(new_document)
        await session.commit()


async def get_document(document_id: int):
    async with session_factory() as session:
        result = await session.get(Documents, document_id)
        return result

async def delete_document(document_id: int):
    async with session_factory() as session:
        query = delete(Documents).where(Documents.id == document_id)
        await session.execute(query)
        await session.commit()
