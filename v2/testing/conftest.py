import pytest
from fastapi.testclient import TestClient
from mongomock_motor import AsyncMongoMockClient
from pymongo import AsyncMongoClient
from testcontainers.mongodb import MongoDbContainer

from src.main import app
from src.configuration.dependencies import get_database


@pytest.fixture(scope="session")
def mongo_container():
	with MongoDbContainer("mongo:latest", port=27017) as mongo:
		yield mongo


@pytest.fixture(scope="session")
def get_database_from_container(mongo_container):
	"""use this for real instance of mongo database. requires docker"""
	mongo_client = AsyncMongoClient(mongo_container.get_connection_url())
	return mongo_client["test_db"]


@pytest.fixture(scope="session")
def get_mocked_database():
	"""use this for a mocked database. does not need docker"""
	client = AsyncMongoMockClient()
	return client["test_db"]


@pytest.fixture(scope="session", autouse=True)
def override_db_dependency(get_database_from_container):
	app.dependency_overrides[get_database] = lambda : get_database_from_container
	yield
	app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def client():
	with TestClient(app) as c:
		yield c


@pytest.fixture(scope="module")
def test_user_and_token(client):
	register_data = {
			"first_name": "test",
			"last_name": "user",
			"email": "test@example.com",
			"password": "TestPass123!"
	}
	resp1 = client.post("/api/auth/register", json=register_data)
	registered_user_data: dict = resp1.json()

	login_data = {
			"username": register_data["email"],
			"password": register_data["password"]
	}
	resp2 = client.post("/api/auth/login", data=login_data)
	token: str = resp2.json()["access_token"]

	return registered_user_data, token