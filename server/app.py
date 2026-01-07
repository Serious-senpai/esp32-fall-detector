from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from .config import ROOT
from .routes import devices_router, events_router, root_router, users_router
from .state import STATE


__all__ = ()


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    await STATE.initialize()
    yield
    await STATE.finalize()


with open(ROOT / "README.md", "r", encoding="utf-8") as f:
    readme = f.read()

app = FastAPI(
    title="ESP32 Fall Detector API",
    description=readme,
    version="0.0.1",
    lifespan=_lifespan,
)
app.include_router(devices_router)
app.include_router(events_router)
app.include_router(root_router)
app.include_router(users_router)
