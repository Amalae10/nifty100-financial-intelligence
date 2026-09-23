import time
from fastapi.testclient import TestClient
from src.api.main import app

client=TestClient(app)

def test_health_response_time():
    start=time.perf_counter()

    response=client.get("api/v1/health")
    elapsed=time.perf_counter() - start

    assert response.status_code==200
    assert elapsed < 1.0

def test_companies_response_time():
    start = time.perf_counter()

    response = client.get("/api/v1/companies")

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert len(response.json()) == 92
    assert elapsed < 1.0

def test_screener_response_time():
    start = time.perf_counter()

    response = client.get("/api/v1/screener?min_roe=15")

    elapsed = time.perf_counter() - start

    assert response.status_code == 200
    assert elapsed < 1.0