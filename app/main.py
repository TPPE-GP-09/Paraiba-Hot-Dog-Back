"""Main application file for the Paraiba Hot Dog API."""
from fastapi import FastAPI
from app.api.v1.routers.users import router as users_router


app = FastAPI(title="Paraiba Hot Dog API")
app.include_router(users_router)

@app.get("/")
def read_root() -> dict[str, str]:
	return {"status": "ok"}