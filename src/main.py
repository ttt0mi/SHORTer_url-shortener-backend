import uvicorn
from fastapi import FastAPI

from src.routes import url_router
from src.configuration.app_config import app_lifespan, configure_cors

app = FastAPI(lifespan=app_lifespan)
configure_cors(app)
app.include_router(url_router.router)

@app.get("/", tags=["root"])
async def root():
	return {"message": "how far OG"}


if __name__ == "__main__":
	uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)