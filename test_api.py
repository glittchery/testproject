import os
import httpx
import pytest

BASE_URL = "http://localhost:8000"
COMMON_WORD = "россии"
NONSENSE_WORD = "zzxqwvkjhgfdsa"


@pytest.fixture(scope="session")
def client():
    with httpx.Client(base_url=BASE_URL, timeout=15) as http_client:
        yield http_client


def search(client, query):
    return client.get("/search", params={"query": query})


def delete(client, document_id):
    return client.delete(f"/documents/{document_id}")


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_returns_documents(client):
    response = search(client, COMMON_WORD)

    assert response.status_code == 200
    assert len(response.json()) > 0


def test_search_returns_at_most_20(client):
    response = search(client, COMMON_WORD)

    assert len(response.json()) <= 20


def test_search_returns_all_db_fields(client):
    documents = search(client, COMMON_WORD).json()

    for document in documents:
        assert set(document) == {"id", "text", "rubrics", "created_date"}
        assert isinstance(document["id"], int)
        assert isinstance(document["text"], str)
        assert isinstance(document["rubrics"], list)


def test_search_sorted_by_date_newest_first(client):
    documents = search(client, COMMON_WORD).json()
    dates = [document["created_date"] for document in documents]

    assert dates == sorted(dates, reverse=True)


def test_search_nothing_found_returns_empty_list(client):
    response = search(client, NONSENSE_WORD)

    assert response.status_code == 200
    assert response.json() == []


def test_search_empty_query_is_rejected(client):
    response = search(client, "")

    assert response.status_code == 422


def test_search_without_query_is_rejected(client):
    response = client.get("/search")

    assert response.status_code == 422


def test_delete_document(client):
    document_id = search(client, COMMON_WORD).json()[0]["id"]
    first = delete(client, document_id)
    second = delete(client, document_id)

    assert first.status_code == 204
    assert second.status_code == 404


def test_deleted_document_is_not_found_by_search(client):
    document_id = search(client, COMMON_WORD).json()[0]["id"]
    delete(client, document_id)
    ids = [document["id"] for document in search(client, COMMON_WORD).json()]
    assert document_id not in ids


def test_delete_unknown_document_returns_404(client):
    response = delete(client, 2147483647)
    assert response.status_code == 404


@pytest.mark.parametrize("bad_id", [0, -1, 2147483648, "abc"])
def test_delete_invalid_id_is_rejected(client, bad_id):
    response = delete(client, bad_id)
    assert response.status_code == 422
