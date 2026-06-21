import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from src.database import get_db
from src.jwt_auth import decode_token
from src.pedidos import repository
from src.pedidos.sse import subscribe, unsubscribe

router = APIRouter()


def _validate_token(token: str) -> None:
    try:
        decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


@router.get("/cozinha/stream/{unidade_id}")
async def stream_cozinha(
    request: Request,
    unidade_id: int = Path(..., gt=0),
    token: str = Query(...),
    db: Session = Depends(get_db),
) -> StreamingResponse:
    _validate_token(token)

    items = repository.listar_cozinha(db, unidade_id)
    initial = json.dumps([item.model_dump() for item in items], default=str)

    async def generate() -> AsyncGenerator[str, None]:
        queue = await subscribe(unidade_id)
        try:
            yield f"data: {initial}\n\n"
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=20.0)
                    yield f"data: {payload}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            unsubscribe(unidade_id, queue)

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
