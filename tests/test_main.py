from fastapi.testclient import TestClient

from ata_api.main import app

client = TestClient(app)


def test_dummy_site():
    response = client.get("/prescription/dummysite/")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Invalid site: dummysite. You also need to specify a user ID",
    }


def test_no_user():
    response = client.get("/prescription/the-19th/")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Please, specify a user ID",
    }


def test_invalid_uuid():
    response = client.get("/prescription/the-19th/dummyuser")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Invalid user ID: dummyuser",
    }


def test_invalid_uuid():
    response = client.get("/prescription/the-19th/dummyuser")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Invalid user ID: dummyuser",
    }


def test_invalid_user_and_site():
    response = client.get("/prescription/dummysite/bc9d39e6-bb74-4bbd-8048-b7ac54054982")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Invalid site: dummysite",
    }
