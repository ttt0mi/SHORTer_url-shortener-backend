from datetime import datetime, timedelta
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pytest
import time_machine

"""
tests may fail on occasions such as rerunning tests due to testcontainers needing time to reload, etc
might add fall back fixture so tests use a mock database if testcontainers fails
add a first parameter to functions that use '@patch' annotation so the patch does not directly disturb the tests
"""

@pytest.mark.parametrize(
		argnames="original_url",
		argvalues=["https://example.com", "https://www.youtube.com/watch?v=EgpLj86ZHFQ"],
		ids=["example", "youtube-link"]
)
def test_create_short_url_text(client, test_user_and_token, original_url):
	_, token = test_user_and_token
	headers = {"Authorization": f"Bearer {token}"}
	payload = {"original_url": original_url}
	resp = client.post("/api/sh/", json=payload, headers=headers)

	assert resp.status_code == 201
	data = resp.json()
	assert "short_url" in data


@patch("secrets.token_urlsafe", return_value="fixed_key123")
def test_get_qr_code_for_original_url(patch_obj, client, test_user_and_token):
	_, token = test_user_and_token
	headers = {"Authorization": f"Bearer {token}"}
	payload = {"original_url": "https://www.youtube.com/watch?v=EgpLj86ZHFQ"}
	create_resp = client.post("/api/sh/", json=payload, headers=headers)
	assert create_resp.status_code == 201

	qr_resp = client.get("/api/sh/qr/fixed_key123", headers=headers)
	assert qr_resp.status_code == 201
	assert qr_resp.headers["content-type"] == "image/png"
	"""
	maybe download pillow to actually check if an image is formed, maybe
	"""


@patch("secrets.token_urlsafe", return_value="fixed_future_key123")
def test_create_short_url_text_with_future_expiry(patch_obj, client, test_user_and_token):
	_, token = test_user_and_token
	headers = {"Authorization": f"Bearer {token}"}

	expires_at = datetime.now(ZoneInfo('UTC')) + timedelta(days=1)
	payload = {
			"original_url": "https://expirytest.com",
			"expires_at": expires_at.isoformat(),
	}
	create_resp = client.post("/api/sh/", json=payload, headers=headers)
	assert create_resp.status_code == 201

	short_url = create_resp.json()["short_url"]
	assert short_url.endswith("fixed_future_key123")

	redirect_resp = client.get(f"/api/sh/fixed_future_key123", follow_redirects=False)
	assert redirect_resp.status_code in (301, 302, 307)
	assert "location" in redirect_resp.headers


@pytest.mark.skip(reason="this test requires mongoDB's TTL functionality to pass")
@patch("secrets.token_urlsafe", return_value="fixed_expired_key123")
def test_create_short_url_text_with_past_expiry(patch_obj, client, test_user_and_token):
	with time_machine.travel("2025-10-05T07:30:00Z", tick=False) as tmt:
		_, token = test_user_and_token
		headers = {"Authorization": f"Bearer {token}"}

		payload = {
				"original_url": "https://expirytest.com",
				"expires_at": datetime.now(ZoneInfo('UTC')).isoformat(),
		}

		create_resp = client.post("/api/sh/", json=payload, headers=headers)
		assert create_resp.status_code == 201

		short_url = create_resp.json()["short_url"]
		assert short_url.endswith("fixed_expired_key123")

		tmt.shift(timedelta(days=1))
		redirect_resp = client.get(f"/api/sh/fixed_expired_key123", follow_redirects=False)
		assert redirect_resp.status_code == 404


@pytest.mark.parametrize(
		argnames=("headers", "expected_status", "reason"),
		argvalues=[
				({}, 401, "missing token"),
				({"Authorization": "Bearer fun4kv3ncn48ui4hur"}, 401, "invalid token"),
		],
		ids=["no-token", "invalid-token"]
)
def test_create_short_url_requires_auth(client, headers, expected_status, reason):
	payload = {"original_url": "https://www.youtube.com/watch?v=EgpLj86ZHFQ"}
	resp = client.post("/api/sh/", json=payload, headers=headers)
	assert resp.status_code == expected_status, f"testing with: {reason}"


@patch("secrets.token_urlsafe", return_value="fixed_key456")
def test_get_short_url_info(patch_obj, client, test_user_and_token):
	with time_machine.travel("2025-10-05T07:30:00Z", tick=False):
		"""this can easily be switched with freeze_time if you prefer that"""
		registered_user, token = test_user_and_token
		headers = {"Authorization": f"Bearer {token}"}

		payload = {"original_url": "https://www.youtube.com/watch?v=EgpLj86ZHFQ"}
		create_resp = client.post("/api/sh/", json=payload, headers=headers)
		assert create_resp.status_code == 201

		short_url = create_resp.json()["short_url"]
		assert short_url.endswith("fixed_key456")

		info_resp = client.get(f"/api/sh/fixed_key456/info", headers=headers)
		assert info_resp.status_code == 200
		info_data = info_resp.json()

		assert info_data == {
				"user_id": registered_user["id"],
				"short_code": "fixed_key456",
				"short_url": short_url,
				"original_url": payload["original_url"],
				"clicks": 0,
				"active": True,
				"created_at": datetime(2025, 10, 5, 7, 30, tzinfo=ZoneInfo('UTC')).strftime('%c'),
				"last_used_at": "Not used",
		}


@patch("secrets.token_urlsafe", return_value="fixed_redirect_key123")
def test_redirect_short_url(patch_obj, client, test_user_and_token):
	_, token = test_user_and_token
	headers = {"Authorization": f"Bearer {token}"}

	payload = {"original_url": "https://www.youtube.com/watch?v=EgpLj86ZHFQ"}
	create_resp = client.post("/api/sh/", json=payload, headers=headers)
	short_url = create_resp.json()["short_url"]
	assert short_url.endswith("fixed_redirect_key123")

	redirect_resp = client.get(f"/api/sh/fixed_redirect_key123", follow_redirects=False)
	assert redirect_resp.status_code in (301, 302, 307)
	assert redirect_resp.is_redirect and redirect_resp.has_redirect_location
	assert redirect_resp.headers['Location'] == "https://www.youtube.com/watch?v=EgpLj86ZHFQ"


def test_get_all_user_urls(client, test_user_and_token):
	_, token = test_user_and_token
	headers = {"Authorization": f"Bearer {token}"}

	urls = ["https://a.com", "https://b.com"]
	for u in urls:
		client.post("/api/sh/", json={"original_url": u}, headers=headers)

	resp = client.get("/api/sh/info/all", headers=headers)
	assert resp.status_code == 200
	data = resp.json()
	assert isinstance(data, list)
	assert all(isinstance(url_info, dict) for url_info in data)

	required_keys = {
			'user_id', 'short_code', 'short_url', 'original_url',
			'clicks', 'active', 'created_at', 'last_used_at'
	}
	assert all(required_keys.issubset(url_info.keys()) for url_info in data)


@patch("secrets.token_urlsafe", return_value="fixed_key78")
def test_disabling_active_short_url(patch_obj, client, test_user_and_token):
	_, token = test_user_and_token
	headers = {"Authorization": f"Bearer {token}"}

	payload = {"original_url": "https://www.youtube.com/watch?v=EgpLj86ZHFQ"}
	create_resp = client.post("/api/sh/", json=payload, headers=headers)
	short_url = create_resp.json()["short_url"]
	assert short_url.endswith("fixed_key78")

	disable_resp = client.patch("/api/sh/disable/fixed_key78", headers=headers)
	assert disable_resp.status_code == 204

	redirect_resp = client.get("/api/sh/fixed_key78")
	assert redirect_resp.status_code == 423


@patch("secrets.token_urlsafe", return_value="fixed_key89")
def test_enabling_disabled_short_url(patch_obj, client, test_user_and_token):
	_, token = test_user_and_token
	headers = {"Authorization": f"Bearer {token}"}

	payload = {"original_url": "https://www.youtube.com/watch?v=EgpLj86ZHFQ"}
	create_resp = client.post("/api/sh/", json=payload, headers=headers)
	short_url = create_resp.json()["short_url"]
	assert short_url.endswith("fixed_key89")

	client.patch("/api/sh/disable/fixed_key89", headers=headers)
	redirect_resp1 = client.get("/api/sh/fixed_key89", follow_redirects=False)
	assert redirect_resp1.status_code == 423

	enable_resp = client.patch("/api/sh/enable/fixed_key89", headers=headers)
	assert enable_resp.status_code == 204
	redirect_resp2 = client.get("/api/sh/fixed_key89", follow_redirects=False)
	assert redirect_resp2.is_redirect and redirect_resp2.has_redirect_location
	assert redirect_resp2.headers["Location"] == payload["original_url"]