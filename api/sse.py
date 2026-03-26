from __future__ import annotations

import asyncio
import json

event_queue: asyncio.Queue = asyncio.Queue()


async def push_event(data: dict) -> None:
    await event_queue.put(data)


async def sse_stream():
    while True:
        data = await event_queue.get()
        yield f"data: {json.dumps(data)}\n\n"
