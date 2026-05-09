"""Main application file for the Paraiba Hot Dog API."""
from fastapi import FastAPI
from app.api.v1.routers.users import router as users_router
from app.api.v1.routers.products import router as products_router


app = FastAPI(title="Paraiba Hot Dog API")
app.include_router(users_router)
app.include_router(products_router)

@app.get("/")
def read_root() -> dict[str, str]:
	return {"status": "ok"}