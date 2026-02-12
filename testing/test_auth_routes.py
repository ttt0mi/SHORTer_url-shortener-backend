import pytest


def test_register_user(client):
	payload = {
			"first_name": "tom",
			"last_name": "smith",
			"email": "tsmith@example.com",
			"password": "TomPass123!"
	}
	resp = client.post("/api/auth/register", json=payload)

	assert resp.status_code == 201
	data = resp.json()
	assert "id" in data
	assert data["email"] == payload["email"]


def test_register_with_duplicate_email(client):
	payload = {
			"first_name": "tom",
			"last_name": "jones",
			"email": "tjones@example.com",
			"password": "TomPass123!"
	}
	resp1 = client.post("/api/auth/register", json=payload)
	assert resp1.status_code == 201

	resp2 = client.post("/api/auth/register", json=payload)
	assert resp2.status_code == 400


def test_login_user(client):
	payload = {
			"first_name": "tom",
			"last_name": "carol",
			"email": "tcoral@example.com",
			"password": "TomPass123!"
	}
	client.post("/api/auth/register", json=payload)

	login_data = {
			"username": payload["email"],
			"password": payload["password"]
	}
	resp = client.post("/api/auth/login", data=login_data)

	assert resp.status_code == 200
	data = resp.json()
	assert "access_token" in data
	assert data["token_type"] == "bearer"


@pytest.mark.parametrize(
		argnames=("username", "password", "expected_status", "reason"),
		argvalues=[
				("nonexistent@example.com", "TomPass123!", 404, "unregistered email"),
				("tcoral@example.com", "WrongPass1@", 401, "invalid password"),
		],
		ids=["unregistered-email", "invalid-password"]
)
def test_login_invalid_cases(client, username, password, expected_status, reason):
	payload = {
			"first_name": "tom",
			"last_name": "carol",
			"email": "tcoral@example.com",
			"password": "TomPass123!"
	}
	client.post("/api/auth/register", json=payload)

	login_data = {
			"username": username,
			"password": password
	}
	resp = client.post("/api/auth/login", data=login_data)

	assert resp.status_code == expected_status, f"testing with: {reason}"


@pytest.mark.parametrize(
		argnames=("headers", "expected_status", "reason"),
		argvalues=[
				({}, 401, "missing token"),
				({"Authorization": "Bearer invalid_token"}, 401, "invalid token"),
		],
		ids=["no-token", "invalid-token"]
)
def test_protected_route_requires_auth(client, headers, expected_status, reason):
	resp = client.get("/api/auth/current", headers=headers)
	assert resp.status_code == expected_status, f"testing with: {reason}"


def test_protected_route_with_token(client, test_user_and_token):
	_, token = test_user_and_token

	headers = {"Authorization": f"Bearer {token}"}
	resp = client.get("/api/auth/current", headers=headers)

	assert resp.status_code == 200
	data = resp.json()
	assert "email" in data
	assert data["email"] == "test@example.com"