from fastapi.testclient import TestClient
from app.main import app
from app.inspector import query_store

client = TestClient(app)

def test_health_and_summary():
    assert client.get('/health').json() == {'status': 'ok'}
    assert 'total_queries' in client.get('/api/summary').json()
    assert isinstance(client.get('/api/queries').json()['items'], list)

def test_dashboard():
    response = client.get('/')
    assert response.status_code == 200
    assert 'Query Perf Inspector' in response.text

def test_n_plus_one_demo_records_queries():
    query_store.clear()
    response = client.post('/api/demo/n-plus-one')
    assert response.status_code == 200
    assert response.json()['mode'] == 'n_plus_one'
    assert client.get('/api/summary').json()['total_queries'] > 0

import pytest


def test_query_count_guard_detects_n_plus_one(query_count_guard):
    with pytest.raises(
        AssertionError,
        match="Repeated SQL statements exceeded",
    ):
        with query_count_guard(max_repeats=2):
            response = client.post("/api/demo/n-plus-one")
            assert response.status_code == 200