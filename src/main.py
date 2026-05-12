from fastapi import FastAPI

from src.produtos.router import router as produtos_router
from src.usuarios.router import router as usuarios_router

app = FastAPI(title="Paraiba Hot Dog API")

app.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])
app.include_router(produtos_router, prefix="/produtos", tags=["produtos"])


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
