from __future__ import annotations

from typing import Optional

import pydantic
from fastapi import APIRouter

from ..codes import INVALID_DISCORD_USER_ID
from ..models import Result, User


__all__ = ("users_router",)
users_router = APIRouter(prefix="/api/users", tags=["users"])


@users_router.get("/{id}", summary="Query a user by ID")
async def get_id(id: int) -> Result[Optional[User]]:
    return await User.get(id=id)


class _PostBody(pydantic.BaseModel):
    username: str
    discord_user_id: str
    password: str


@users_router.post("/", summary="Create a new user")
async def post(body: _PostBody) -> Result[Optional[User]]:
    try:
        discord_user_id = int(body.discord_user_id)
        return await User.create(
            username=body.username,
            discord_user_id=discord_user_id,
            password=body.password,
        )

    except ValueError:
        return Result(code=INVALID_DISCORD_USER_ID, data=None)
