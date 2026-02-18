from src.configuration.app_factory import create_app

app = create_app(
	title="Url Shortener",
	summary="application for shortening URLs",
	lifespan=True,
	cors=True,
	trusted_hosts=True
)


@app.get("/", tags=["root"])
async def root():
	return {"message": "how far OG"}


if __name__ == "__main__":
	import os
	import uvicorn
	
	port = int(os.getenv("PORT", 8000))
	uvicorn.run(
		"src.main:app", host="0.0.0.0",
		port=port, timeout_graceful_shutdown=30
	)