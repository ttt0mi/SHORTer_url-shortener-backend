from fastapi import FastAPI

from src.configuration.app_config import app_lifespan, configure_cors, register_routes


def create_app(title: str, summary: str) -> FastAPI:
	app = FastAPI(
			title=title, summary=summary,
			lifespan=app_lifespan, debug=True
	)
	configure_cors(app)
	register_routes(app)
	return app