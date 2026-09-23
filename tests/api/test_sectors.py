from fastapi.testclient import TestClient
from src.api.main import app

client=TestClient(app)

def test_sectors_count():
    respnse=client.get("/api/v1/sectors")
    assert respnse.status_code==200
    assert len(respnse.json())==10

def test_information_technology_sector():
    response=client.get("/api/v1/sectors/Information%20Technology/companies")

    assert response.status_code==200

    data=response.json()
    assert len(data) > 0

    for company in data:
        assert company["sector"]=="Information Technology"

def test_invalid_sector():
    response=client.get("/api/v1/sectors/InvalidSector/companies")
    assert response.status_code==404