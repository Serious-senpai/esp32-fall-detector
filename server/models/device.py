from __future__ import annotations

from typing import Annotated, List, Optional, Self

import asyncpg  # type: ignore
import pydantic

from .result import Result
from .snowflake import Snowflake
from .user import User
from ..codes import DATABASE_FAILURE, DEVICE_NOT_FOUND
from ..state import STATE


__all__ = ("Device",)


class Device(Snowflake):
    """Represents a device"""

    name: Annotated[str, pydantic.Field(description="The device name")]
    hashed_token: Annotated[str, pydantic.Field(description="The hashed token")]
    user: Annotated[User, pydantic.Field(description="The device owner")]

    @classmethod
    def from_row(cls, row: asyncpg.Record) -> Self:
        return cls(
            id=row["device_id"],
            name=row["device_name"],
            hashed_token=row["device_hashed_token"],
            user=User.from_row(row),
        )

    @classmethod
    async def get(cls, *, id: int) -> Result[Optional[Self]]:
        pool = await STATE.database.get_pool()
        if pool is None:
            return Result(code=DATABASE_FAILURE, data=None)

        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM view_devices WHERE device_id = $1", id)
            if row is None:
                return Result(code=DEVICE_NOT_FOUND, data=None)

            return Result(data=cls.from_row(row))

    @classmethod
    async def get_all(cls, *, user_id: int) -> Result[List[Self]]:
        pool = await STATE.database.get_pool()
        if pool is None:
            return Result(code=DATABASE_FAILURE, data=[])

        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM view_devices WHERE user_id = $1", user_id)
            devices = [cls.from_row(row) for row in rows]
            return Result(data=devices)

    @classmethod
    async def create(cls, *, name: str, token: str, user_id: int) -> Result[Optional[Self]]:
        hashed = STATE.hasher.hash(token)
        pool = await STATE.database.get_pool()
        if pool is None:
            return Result(code=DATABASE_FAILURE, data=None)

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM create_device($1, $2, $3)",
                name,
                hashed,
                user_id,
            )

            return Result(data=cls.from_row(row))
