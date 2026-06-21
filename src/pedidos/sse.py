import asyncio
from collections import defaultdict

_subscribers: dict[int, list[asyncio.Queue]] = defaultdict(list)


async def subscribe(unidade_id: int) -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue(maxsize=20)
    _subscribers[unidade_id].append(queue)
    return queue


def unsubscribe(unidade_id: int, queue: asyncio.Queue) -> None:
    try:
        _subscribers[unidade_id].remove(queue)
    except ValueError:
        pass


async def broadcast(unidade_id: int, payload: str) -> None:
    for queue in list(_subscribers.get(unidade_id, [])):
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            pass
