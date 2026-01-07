from __future__ import annotations

import traceback
from typing import Dict, Optional, TYPE_CHECKING

import aiohttp
from argon2 import PasswordHasher

from .config import (
    DISCORD_API_URL,
    DISCORD_BOT_TOKEN,
    POSTGRES_DB,
    POSTGRES_HOST,
    POSTGRES_PASSWORD,
    POSTGRES_USER,
)
from .database import DatabaseConnector


__all__ = ("ApplicationState", "STATE")


class ApplicationState:

    __slots__ = (
        "_http",
        "database",
        "hasher",
        "discord_auth_header",
        "discord_avatar_url",
    )
    if TYPE_CHECKING:
        _http: Optional[aiohttp.ClientSession]
        database: DatabaseConnector
        hasher: PasswordHasher
        discord_auth_header: Dict[str, str]
        discord_avatar_url: Optional[str]

    def __init__(self, *, database: DatabaseConnector) -> None:
        self._http = None
        self.database = database
        self.hasher = PasswordHasher()
        self.discord_auth_header = {
            "Authorization": f"Bot {DISCORD_BOT_TOKEN}",
        }
        self.discord_avatar_url = None

    @property
    def http(self) -> aiohttp.ClientSession:
        if self._http is None:
            self._http = aiohttp.ClientSession()

        return self._http

    async def initialize(self) -> None:
        self._http = aiohttp.ClientSession()

        try:
            async with self._http.get(
                DISCORD_API_URL.joinpath("users/@me"),
                headers=self.discord_auth_header,
            ) as response:
                if response.status == 200:
                    data = await response.json(encoding="utf-8")
                    id = data["id"]
                    avatar = data["avatar"]
                    self.discord_avatar_url = f"https://cdn.discordapp.com/avatars/{id}/{avatar}.png" if avatar is not None else None

        except Exception:
            traceback.print_exc()
            self.discord_avatar_url = None

        await self.database.get_pool()

    async def finalize(self) -> None:
        if self._http is not None:
            await self._http.close()

        await self.database.close()


STATE = ApplicationState(
    database=DatabaseConnector(
        database=POSTGRES_DB,
        host=POSTGRES_HOST,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
    ),
)
