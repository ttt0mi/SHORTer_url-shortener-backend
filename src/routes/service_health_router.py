import os
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter
from starlette.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE


router = APIRouter(tags=["Render Health Checks"])

def get_async_mongo_client():
	from src.configuration.database_config import mongo_client
	if not mongo_client:
		raise Exception("MongoDB async client not configured")
	return mongo_client


@router.get("/health", status_code=HTTP_200_OK)
async def health_check():
	"""
	Health check endpoint required by Render.

	Render uses this to determine if the service is ready to receive traffic.
	Returns 200 if healthy, 503 if unhealthy.
	"""
	print("HEALTH: entered")
	health_status = {
		"status": "healthy",
		"timestamp": datetime.now(ZoneInfo('UTC')).isoformat(),
		"service": "SHORTer_url-shortener-backend",
		"checks": {}
	}
	
	#check 1: api can be reached
	health_status["checks"]["api"] = "ok"
	print("HEALTH: checking environment")
	#check 2: existence of environment variables
	required_env_vars = {"DATABASE_URI", "TOKEN_KEY", "ALLOWED_HOSTS", "ALLOWED_ORIGINS"}
	missing_env_vars = {var for var in required_env_vars if not os.getenv(var)}
	
	if missing_env_vars:
		print("HEALTH: missing environment vars")
		health_status["status"] = "unhealthy"
		health_status["checks"]["environment"] = f"missing: {', '.join(sorted(missing_env_vars))}"
		return JSONResponse(
			status_code=HTTP_503_SERVICE_UNAVAILABLE,
			content=health_status
		)
	
	health_status["checks"]["environment"] = "ok"

	#check 3. database connectivity
	try:
		print("HEALTH: getting Mongo client")
		client = get_async_mongo_client()
		print("HEALTH: got Mongo client")
		print("HEALTH: pinging Mongo")
		await client.admin.command("ping", maxTimeMS=5000)
		health_status["checks"]["database"] = "connected"
		print("HEALTH: Mongo ping successful")
	except Exception as e:
		print(f"HEALTH: Mongo error: {e}")
		health_status["status"] = "unhealthy"
		health_status["checks"]["database"] = f"disconnected: {str(e)}"
		return JSONResponse(
			status_code=HTTP_503_SERVICE_UNAVAILABLE, content=health_status
		)
	
	return health_status