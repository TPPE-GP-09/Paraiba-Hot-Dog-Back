from fastapi import FastAPI

from src.usuarios.router import router as usuarios_router
from src.produtos.router import router as produtos_router
from src.unidades.router import router as unidades_router
from src.permissoes.router import router as permissoes_router
from src.pedidos.router import router as pedidos_router

app = FastAPI(title="Paraiba Hot Dog API")

app.include_router(usuarios_router, prefix="/usuarios", tags=["usuarios"])
app.include_router(produtos_router, prefix="/produtos", tags=["produtos"])
app.include_router(unidades_router, prefix="/unidades", tags=["unidades"])
app.include_router(permissoes_router, prefix="/permissoes", tags=["permissoes"])
app.include_router(pedidos_router, prefix="/pedidos", tags=["pedidos"])


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "ok"}
