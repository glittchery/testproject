import csv
import os
import ast
from datetime import datetime
from sqlalchemy import select, func
from src.database.models import Documents
from src.database.database import session_factory
from src.database.queries import get_documents, delete_document_db
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from fastapi import Response

es = AsyncElasticsearch(os.environ["ELASTICSEARCH_HOST"])

async def create_index():
    exists = await es.indices.exists(index="documents")

    if not exists:
        await es.indices.create(
            index="documents",
            mappings={
                "properties": {
                    "id": {
                        "type": "integer"
                    },
                    "text": {
                        "type": "text",
                        "analyzer": "russian"
                    }
                }
            }
        )

async def es_client_close():
    await es.close()

async def insert_documents():
    async with session_factory() as session:
        count = await session.scalar(select(func.count()).select_from(Documents))
        if count:
            return
    documents = []
    with open("posts.csv", "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            documents.append(
                Documents(
                    text=row["text"],
                    rubrics=ast.literal_eval(row["rubrics"]),
                    created_date=datetime.strptime(row["created_date"],"%Y-%m-%d %H:%M:%S")
                )
            )

        async with session_factory() as session:
            session.add_all(documents)
            await session.flush()

            actions = [
                {
                    "_index": "documents",
                    "_id": document.id,
                    "_source": {
                        "id": document.id,
                        "text": document.text
                    }
                }
                for document in documents
            ]

            await async_bulk(es, actions)
            await session.commit()


async def search_documents(query: str):
    elastic_response = await es.search(
        index="documents",
        query={
            "match": {
                "text": query
            }
        },
        size=20
    )
    ids = [hit["_source"]["id"] for hit in elastic_response["hits"]["hits"]]
    db_response = await get_documents(ids)
    db_response = sorted(db_response, key=lambda document: document.created_date, reverse=True)

    return db_response

async def delete_document(document_id):
    await delete_document_db(document_id)
    await es.options(ignore_status=404).delete(index="documents", id=document_id)
    return Response(status_code=204)



