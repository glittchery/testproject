from src.database.database import engine, Base, session_factory
from src.database.models import Documents
from sqlalchemy import delete, select
from datetime import datetime

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# get element
# delete element


async def get_documents(ids: list[int]):
    async with session_factory() as session:
        result = await session.execute(
            select(Documents)
            .where(Documents.id.in_(ids))
        )

        return result.scalars().all()

async def delete_document_db(document_id: int):
    async with session_factory() as session:
        query = delete(Documents).where(Documents.id == document_id)
        await session.execute(query)
        await session.commit()
