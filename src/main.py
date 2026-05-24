from fastapi import Depends, FastAPI

from src.clientes.router import router as clientes_router
from src.usuarios.router import router as usuarios_router
from src.produtos.router import router as produtos_router
from src.unidades.router import router as unidades_router
from src.permissoes.router import router as permissoes_router
from src.blog.router import router as blog_router
from src.pedidos.router import router as pedidos_router
from src.security import get_current_user

app = FastAPI(title="Paraiba Hot Dog API")

auth_dependencies = [Depends(get_current_user)]

app.include_router(
    clientes_router,
    prefix="/clientes",
    tags=["clientes"],
    dependencies=auth_dependencies,
)
app.include_router(
    usuarios_router,
    prefix="/usuarios",
    tags=["usuarios"],
    dependencies=auth_dependencies,
)
app.include_router(
    produtos_router,
    prefix="/produtos",
    tags=["produtos"],
)
app.include_router(
    unidades_router,
    prefix="/unidades",
    tags=["unidades"],
)
app.include_router(
    permissoes_router,
    prefix="/permissoes",
    tags=["permissoes"],
    dependencies=auth_dependencies,
)
app.include_router(
    blog_router,
    prefix="/blog",
    tags=["blog"],
)
app.include_router(
    pedidos_router,
    prefix="/pedidos",
    tags=["pedidos"],
    dependencies=auth_dependencies,
)


@app.get("/")
def read_root() -> dict[str, str]:
    """Verifica se a API esta em execucao e retorna o status de saude."""
    return {"status": "ok"}
