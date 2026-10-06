import csv
from src.database.models import Documents
from src.database.database import session_factory
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

es = AsyncElasticsearch("http://elasticsearch:9200")

async def create_index():
    exists = await es.indices.exists(index="documents")

    if not exists:
        await es.indices.create(
            index="documnets",
            mappings={
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "text": {
                        "type": "text"
                    }
                }
            }
        )

async def insert_documents():
    documents = []
    with open("posts.csv", "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            documents.append(
                Documents(
                    text=row["text"],
                    rubrics=row["rubrics"],
                    created_date=row["created_date"]
                )
            )

        async with session_factory() as session:
            session.add_all(documents)
            await session.flush()

            actions = [
                {
                    "_index": "documents",
                    "_source": {
                        "id": document.id,
                        "text": document.text
                    }
                }
                for document in documents
            ]

            await session.commit()
            await async_bulk(es, actions)




