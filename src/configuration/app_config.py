from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from src.configuration.settings import get_settings
from src.routes import urls_router, service_health_router
from src.routes import authentication_router
from src.configuration.database_config import connect, disconnect


def configure_cors(app: FastAPI):
	app.add_middleware(
			CORSMiddleware,
			allow_origins=get_settings().allowed_origins,
			#an origin is a string = f"{protocol}://{domain}:{port}". the port is optional
			#protocols like http, https; domains like myapp.com, localhost;  ports like 443, 8080, 80
			allow_credentials=True,
			#this allows authorisations like bearer tokens, cookies, etc.
			#if set to true, all other methods cannot use wildcards
			allow_methods=["*"],
			allow_headers=["*"],
			#these are the "simple" cors headers. they are usually sent automatically when "allow_credentials=False"
			#we have to list them out otherwise, plus I added the "Authorization" header for bearer tokens & cookies for refresh tokens
	)

def configure_trusted_hosts(app: FastAPI):
	app.add_middleware(
		TrustedHostMiddleware,
		allowed_hosts=get_settings().allowed_hosts,
	)

@asynccontextmanager
async def app_lifespan(app: FastAPI):
	"""an async context manager for starting and stopping the application lifecycle.
		when this context is entered, it attempts to connect to the database using a 'connect()' function described in database_config.py.
		When this context is exited, it attempts to disconnect from the database client using a 'disconnect()' function described in database_config.py.
		If an exception occurs anywhere within the context, it raises an exception."""
	await connect()
	yield
	await disconnect()

def register_routes(app: FastAPI):
	app.include_router(authentication_router.router)
	app.include_router(urls_router.router)
	app.include_router(service_health_router.router)