import uvicorn

from src.configuration.app_factory import create_app

app = create_app(title = "Url Shortener", summary="application for shortening URLs")


@app.get("/", tags=["root"])
async def root():
	return {"message": "how far OG"}


if __name__ == "__main__":
	uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)