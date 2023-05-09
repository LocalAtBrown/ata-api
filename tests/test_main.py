from fastapi.testclient import TestClient
from fastapi import status

from ata_api.main import app

client = TestClient(app)


def test_invalid_user_id() -> None:
    response = client.get("/prescription/the-19th/dummyuser")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid user ID: dummyuser",
    }


def test_invalid_site_name() -> None:
    response = client.get("/prescription/dummysite/bc9d39e6-bb74-4bbd-8048-b7ac54054982")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        "detail": "Invalid site: dummysite",
    }
