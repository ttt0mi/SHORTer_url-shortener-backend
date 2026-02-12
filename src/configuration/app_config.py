from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.configuration.database_config import connect, disconnect


def configure_cors(app: FastAPI):
	app.add_middleware(
			CORSMiddleware,
			allow_origins=["*"],		#add frontend url after
			allow_credentials=False,
			allow_methods=["*"],
			allow_headers=["*"],
	)


@asynccontextmanager
async def app_lifespan(app: FastAPI):
	connect()
	yield
	disconnect()


"""
	an async context manager for starting and stopping the application lifecycle.
	when the context is entered, it attempts to connect to the database using a 'connect()' function described in database_config.py.
	When the context is exited, it attempts to disconnect from the database client using a 'disconnect()' function described in database_config.py.
	If an exception occurs anywhere within the context, it raises an exception.
	
	edited: This is out of date
"""