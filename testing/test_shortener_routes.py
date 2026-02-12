from datetime import datetime, UTC, timedelta
from unittest.mock import patch

from starlette import status

#maybe add a setup and teardown cause this shit isn't working together


@patch("src.utilities.code_utils.token_urlsafe", return_value="fixed_key123")
def test_post_original_url_to_get_shortened(patched_token ,client):
	response = client.post("/shorter/", json={'original_url': "https://example.com"})
	assert response.status_code == status.HTTP_201_CREATED
	data = response.json()
	assert list(data.keys()) == ['short_url', 'secret_key']
	assert data['short_url'] == f"http://testserver/shorter/fixed_key123"
	assert data['secret_key'] == "fixed_key123fixed_key123"


@patch("src.utilities.code_utils.token_urlsafe", return_value="fixed_key234")
def test_get_short_url_returns_redirect(patched_token, client):
	res1 = client.post("/shorter/", json={'original_url': "https://example.com"})
	data = res1.json()
	assert data['short_url'] == "http://testserver/shorter/fixed_key234"

	res2 = client.get(data['short_url'], follow_redirects=False)
	assert res2.is_redirect is True
	assert res2.headers['Location'] == "https://example.com/"


def test_post_secret_key_to_get_info(client):
	with patch("src.utilities.code_utils.token_urlsafe", return_value="fixed_key456"):
		res1 = client.post("/shorter/", json={'original_url': "https://example.com"})
		data1 = res1.json()
		assert data1['secret_key'] == "fixed_key456fixed_key456"

		res2 = client.get(f"/shorter/info/{data1['secret_key']}")
		assert res2.status_code == status.HTTP_200_OK
		data2 = res2.json()
		current_time = (datetime.now(UTC) - timedelta(microseconds=10)).strftime('%Y-%m-%d %H:%M:%S')
		assert data2 == {
				'short_url': "http://testserver/shorter/fixed_key456",
				'original_url': "https://example.com/",
				'clicks': 0,
				'active': True,
				'created_at': current_time,
				'last_used_at': "Not used",
				'secret_key': "fixed_key456fixed_key456"
		}


def test_post_secret_key_to_disable_short_url(client):
	with patch("src.utilities.code_utils.token_urlsafe", return_value="fixed_key567"):
		res1 = client.post("/shorter/", json={'original_url': "https://example.com"})
		data1 = res1.json()
		assert data1['secret_key'] == "fixed_key567fixed_key567"

		res2 = client.patch(f"/shorter/disable/{data1['secret_key']}")
		assert res2.status_code == status.HTTP_204_NO_CONTENT

		res3 = client.get(f"/shorter/info/{data1['secret_key']}")
		assert res3.status_code == status.HTTP_423_LOCKED


def test_post_secret_key_to_enable_short_url(client):
	with patch("src.utilities.code_utils.token_urlsafe", return_value="fixed_key789"):
		res1 = client.post("/shorter/", json={'original_url': "https://example.com"})
		data1 = res1.json()
		assert data1['secret_key'] == "fixed_key789fixed_key789"

		res2 = client.patch(f"/shorter/disable/{data1['secret_key']}")
		assert res2.status_code == status.HTTP_204_NO_CONTENT

		res3 = client.get(f"/shorter/info/{data1['secret_key']}")
		assert res3.status_code == status.HTTP_423_LOCKED

		res4 = client.patch(f"/shorter/enable/{data1['secret_key']}")
		assert res4.status_code == status.HTTP_204_NO_CONTENT

		res5 = client.get(f"/shorter/info/{data1['secret_key']}")
		assert res5.status_code == status.HTTP_200_OK
		data2 = res5.json()
		assert data2['active'] is True






# install pytest-asyncio
# import pytest(to use "mocker")
# from unittest.mock import AsyncMock
#
# decorate async tests with @pytest.mark.asyncio

# example:-
# @pytest.mark.asyncio
# async def test_read_user_success(mocker):
#    mock_get_user = mocker.patch(
#         "src.main.get_user",
#         new_callable=AsyncMock,
#         return_value={"id": 1, "name": "Mock User"}
#     )

#     with TestClient(app) as client:
#         response = client.get("/users/1")

#     assert response.status_code == 200
#     assert response.json() == {"id": 1, "name": "Mock User"}
#     mock_get_user.assert_awaited_once_with(1)