from mongomock_motor import AsyncMongoMockClient

import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.configuration.database_config import get_database


@pytest.fixture(scope="session")
def get_test_database():
	mongo_client = AsyncMongoMockClient()
	return mongo_client["test_db"]


@pytest.fixture(scope="session", autouse=True)
def override_db_dependency(get_test_database):
	app.dependency_overrides[get_database] = lambda : get_test_database
	yield
	app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client():
	with TestClient(app) as c:
		yield c