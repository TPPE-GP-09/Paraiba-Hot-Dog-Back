"""Main application file for the Paraiba Hot Dog API."""
from fastapi import FastAPI
from app.api.v1.routers.usuarios import router as usuarios_router
from app.api.v1.routers.produtos import router as produtos_router


app = FastAPI(title="Paraiba Hot Dog API")
app.include_router(usuarios_router)
app.include_router(produtos_router)

@app.get("/")
def read_root() -> dict[str, str]:
	return {"status": "ok"}
