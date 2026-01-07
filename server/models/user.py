from __future__ import annotations

import asyncio
from typing import Annotated, List, Optional, Self

import asyncpg  # type: ignore
import pydantic
from asyncpg.exceptions import UniqueViolationError  # type: ignore

from .discord import Embed
from .result import Result
from .snowflake import Snowflake
from ..codes import (
    DATABASE_FAILURE,
    DISCORD_API_ERROR,
    DUPLICATE_USERNAME,
    INCORRECT_CREDENTIALS,
    INVALID_DISCORD_USER_ID,
    USER_NOT_FOUND,
)
from ..config import DISCORD_API_URL
from ..state import STATE


__all__ = ("User",)


class User(Snowflake):
    """Represents a user"""

    username: Annotated[str, pydantic.Field(description="The username")]
    discord_channel_id: Annotated[int, pydantic.Field(description="The ID of the Discord user DM channel")]
    hashed_password: Annotated[str, pydantic.Field(description="The hashed password")]

    async def send(
        self,
        content: Optional[str] = None,
        embeds: Optional[List[Embed]] = None,
    ) -> Result[None]:
        payload = {
            "content": content,
            "embeds": [embed.model_dump() for embed in embeds] if embeds is not None else None,
        }
        async with STATE.http.post(
            DISCORD_API_URL.joinpath(f"channels/{self.discord_channel_id}/messages"),
            json=payload,
            headers=STATE.discord_auth_header,
        ) as response:
            if response.status == 200:
                return Result(data=None)
            else:
                return Result(code=DISCORD_API_ERROR, data=None)

    @staticmethod
    async def _create_dm_channel(discord_user_id: int) -> Result[Optional[int]]:
        async with STATE.http.post(
            DISCORD_API_URL.joinpath(f"users/@me/channels"),
            json={"recipient_id": str(discord_user_id)},
            headers=STATE.discord_auth_header,
        ) as response:
            if response.status == 200:
                data = await response.json(encoding="utf-8")
                discord_channel_id = int(data["id"])
                return Result(data=discord_channel_id)
            else:
                return Result(code=INVALID_DISCORD_USER_ID, data=None)

    @classmethod
    def from_row(cls, row: asyncpg.Record) -> Self:
        return cls(
            id=row["user_id"],
            username=row["user_username"],
            discord_channel_id=row["user_discord_channel_id"],
            hashed_password=row["user_hashed_password"],
        )

    @classmethod
    async def get(cls, *, id: int) -> Result[Optional[Self]]:
        pool = await STATE.database.get_pool()
        if pool is None:
            return Result(code=DATABASE_FAILURE, data=None)

        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM view_users WHERE user_id = $1", id)
            if row is None:
                return Result(code=USER_NOT_FOUND, data=None)

            return Result(data=cls.from_row(row))

    @classmethod
    async def login(cls, *, username: str, password: str) -> Result[Optional[Self]]:
        pool = await STATE.database.get_pool()
        if pool is None:
            return Result(code=DATABASE_FAILURE, data=None)

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM view_users WHERE user_username = $1",
                username,
            )
            if row is None:
                return Result(code=INCORRECT_CREDENTIALS, data=None)

            user = cls.from_row(row)
            try:
                STATE.hasher.verify(user.hashed_password, password)

            except Exception:
                return Result(code=INCORRECT_CREDENTIALS, data=None)

            async def _rehash_task() -> None:
                if STATE.hasher.check_needs_rehash(user.hashed_password):
                    new_hashed = STATE.hasher.hash(password)
                    async with pool.acquire() as conn:
                        await conn.execute(
                            "UPDATE Users SET hashed_password = $1 WHERE id = $2",
                            new_hashed,
                            user.id,
                        )

            asyncio.create_task(_rehash_task())
            return Result(data=user)

    @classmethod
    async def create(cls, *, username: str, discord_user_id: int, password: str) -> Result[Optional[Self]]:
        hashed = STATE.hasher.hash(password)
        pool = await STATE.database.get_pool()
        if pool is None:
            return Result(code=DATABASE_FAILURE, data=None)

        discord_channel_id = await cls._create_dm_channel(discord_user_id)
        if discord_channel_id.data is None:
            return Result(code=discord_channel_id.code, data=None)

        async with pool.acquire() as conn:
            try:
                row = await conn.fetchrow(
                    "SELECT * FROM create_user($1, $2, $3)",
                    username,
                    discord_channel_id.data,
                    hashed,
                )

                return Result(data=cls.from_row(row))

            except UniqueViolationError:
                return Result(code=DUPLICATE_USERNAME, data=None)
