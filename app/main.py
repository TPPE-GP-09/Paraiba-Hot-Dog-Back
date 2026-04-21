from fastapi import FastAPI


app = FastAPI(title="Paraiba Hot Dog API")


@app.get("/")
def read_root() -> dict[str, str]:
	return {"status": "ok"}
