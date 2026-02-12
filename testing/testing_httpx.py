import httpx

def get_data():
    # response = httpx.get("https://httpbin.org/get")
    response = httpx.get("http://127.0.0.1:8000")
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Content: {response.text}")
    print(f"json: {response.json()}")
    return response


def create_task():
    url = "https://httpbin.org/post"
    payload = {"title": "Learn HTTPX", "completed": False}
    response = httpx.post(url, json=payload)

    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    return response

if __name__ == "__main__":
    get_data()
    create_task()