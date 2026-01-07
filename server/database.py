from __future__ import annotations

import asyncio
import traceback
from typing import Optional, TYPE_CHECKING

import asyncpg  # type: ignore  # asyncpg does not provide type stubs

from .config import ROOT


__all__ = ("DatabaseConnector",)


class DatabaseConnector:

    __slots__ = (
        "_pool",
        "_lifecycle_lock",
        "_database",
        "_host",
        "_user",
        "_password",
    )
    if TYPE_CHECKING:
        _pool: Optional[asyncpg.Pool]
        _lifecycle_lock: asyncio.Lock
        _database: str
        _host: str
        _user: str
        _password: str

    def __init__(self, *, database: str, host: str, user: str, password: str) -> None:
        self._pool = None
        self._lifecycle_lock = asyncio.Lock()
        self._database = database
        self._host = host
        self._user = user
        self._password = password

    async def get_pool(self) -> Optional[asyncpg.Pool]:
        try:
            await asyncio.wait_for(self._lifecycle_lock.acquire(), timeout=3)
        except asyncio.TimeoutError:
            return self._pool

        try:
            if self._pool is not None:
                return self._pool

            self._pool = pool = await asyncpg.create_pool(
                database=self._database,
                host=self._host,
                user=self._user,
                password=self._password,
            )

            async with pool.acquire() as conn:
                script = ROOT / "scripts"
                for file in ["tables.sql", "functions.sql", "views.sql"]:
                    path = script / file
                    await conn.execute(path.read_text(encoding="utf-8"))

            return pool

        except Exception:
            traceback.print_exc()
            self._pool = None
            return None

        finally:
            self._lifecycle_lock.release()

    async def close(self) -> None:
        await asyncio.wait_for(self._lifecycle_lock.acquire(), timeout=3)
        try:
            pool = self._pool
            self._pool = None

        finally:
            self._lifecycle_lock.release()

        if pool is not None:
            await pool.close()
