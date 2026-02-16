from fastapi import FastAPI

from src.configuration.app_config import app_lifespan, configure_cors, register_routes, configure_trusted_hosts


def create_app(title: str, summary: str, *, lifespan: bool, debug: bool, cors: bool, trusted_hosts: bool) -> FastAPI:
	app = FastAPI(
		title=title, summary=summary,
		lifespan=app_lifespan if lifespan else None,
		debug=debug
	)
	register_routes(app)

	if cors:
		configure_cors(app)
	if trusted_hosts:
		configure_trusted_hosts(app)
	
	return app