"""Main application file for the Paraiba Hot Dog API."""
from fastapi import FastAPI
from app.api.v1.routers.usuarios import router as usuarios_router
from app.api.v1.routers.produtos import router as produtos_router

app = FastAPI(title="Paraiba Hot Dog API")

# Adicione os prefixos e as tags aqui:
app.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])
app.include_router(produtos_router, prefix="/produtos", tags=["produtos"])

@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}