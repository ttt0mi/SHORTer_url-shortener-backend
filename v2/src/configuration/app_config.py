from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.routes import urls_router
from src.routes import authentication_router
from src.configuration.database_config import connect, disconnect


def configure_cors(app: FastAPI):
	app.add_middleware(
			CORSMiddleware,
			allow_origins=["http://localhost:1234"],
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


@asynccontextmanager
async def app_lifespan(app: FastAPI):
	await connect()
	yield
	await disconnect()

"""
	an async context manager for starting and stopping the application lifecycle.
	when the context is entered, it attempts to connect to the database using a 'connect()' function described in database_config.py.
	When the context is exited, it attempts to disconnect from the database client using a 'disconnect()' function described in database_config.py.
	If an exception occurs anywhere within the context, it raises an exception.
	
	edited: This is out of date
"""


def register_routes(app: FastAPI):
	app.include_router(authentication_router.router)
	app.include_router(urls_router.router)