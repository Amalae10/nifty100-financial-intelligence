import time
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)


def make_request(_):
    start = time.perf_counter()
    response = client.get("/api/v1/health")
    latency = time.perf_counter() - start
    return response.status_code, latency


def test_50_concurrent_requests():
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(make_request, range(50)))

    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results]

    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)

    print(f"\nRequests: 50")
    print(f"Successful: {statuses.count(200)}")
    print(f"Average latency: {avg_latency:.4f}s")
    print(f"Maximum latency: {max_latency:.4f}s")

    assert all(status == 200 for status in statuses)