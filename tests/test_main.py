from typing import Generator, Tuple
from uuid import UUID

import pytest
from ata_db_models.models import Group, SQLModel, UserGroup
from fastapi import status
from fastapi.testclient import TestClient

from ata_api.helpers.enums import SiteName
from ata_api.main import app, engine, session_factory

client = TestClient(app)


@pytest.fixture(scope="function")
def create_and_drop_tables() -> Generator[None, None, None]:
    """
    Fixture responsible for creating tables before and dropping tables after
    every test, ensuring a clean slate. (See: https://docs.pytest.org/en/6.2.x/fixture.html#:~:text=%E2%80%9CYield%E2%80%9D%20fixtures%20yield%20instead%20of,is%20swapped%20out%20for%20yield%20.)

    If using a dedicated test DB instead of localhost, try the https://dev.to/jbrocher/fastapi-testing-a-database-5ao5 approach,
    which right now is overkill.
    """
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


class TestRoot:
    @pytest.mark.unit
    def test_root(self) -> None:
        response = client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "This is the root endpoint for the AtA API."}


class TestPrescription:
    @pytest.fixture(scope="class")
    def user(self) -> Tuple[str, str]:
        return (SiteName.AFRO_LA, "3800ac11781a4cf2a6759bbaa9c0729b")

    @pytest.mark.unit
    def test_invalid_user_id(self, user: Tuple[str, str]) -> None:
        response = client.get(f"/prescription/{user[0]}/dummyuser")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "value is not a valid uuid" in response.json()["detail"][0]["msg"]

    @pytest.mark.unit
    def test_invalid_site_name(self, user: Tuple[str, str]) -> None:
        response = client.get(f"/prescription/dummysite/{user[1]}")
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "value is not a valid enumeration member" in response.json()["detail"][0]["msg"]

    @pytest.mark.integration
    def test_user_missing(self, create_and_drop_tables: Generator[None, None, None], user: Tuple[str, str]) -> None:
        """
        If a valid user (valid ID & site name) doesn't already exist, they
        should be created.
        """
        response = client.get(f"/prescription/{'/'.join(user)}")
        assert response.status_code == status.HTTP_200_OK

        # Check returned data is of the right user
        data = response.json()
        assert data["site_name"] == user[0]
        assert UUID(data["user_id"]) == UUID(user[1])
        assert data["group"] in {*Group}  # A, B or C

        # Check user is written to table
        with session_factory() as session:
            count = session.query(UserGroup).count()
            assert count == 1

    @pytest.mark.integration
    def test_user_exists(self, create_and_drop_tables: Generator[None, None, None], user: Tuple[str, str]) -> None:
        """
        If a valid user (valid ID & site name) already exists, they should
        simply be returned.
        """
        # First, write user to DB
        with session_factory() as session:
            usergroup = UserGroup(site_name=user[0], user_id=user[1], group=Group.A)
            session.add(usergroup)
            session.commit()

        # Check that user is written
        with session:
            count = session.query(UserGroup).count()
            assert count == 1

        # Make endpoint call
        response = client.get(f"/prescription/{'/'.join(user)}")
        assert response.status_code == status.HTTP_200_OK

        # Check returned data is of the right user
        data = response.json()
        assert data["site_name"] == user[0]
        assert UUID(data["user_id"]) == UUID(user[1])
        assert data["group"] in {*Group}  # A, B or C
