from __future__ import annotations

from typing import Optional

import pydantic
from fastapi import APIRouter

from ..models import Result, User


__all__ = ("users_router",)
users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get("/{id}", summary="Query a user by ID")
async def get_id(id: int) -> Result[Optional[User]]:
    return await User.get(id=id)


class _PostBody(pydantic.BaseModel):
    username: str
    discord_user_id: int
    password: str


@users_router.post("/", summary="Create a new user")
async def post(body: _PostBody) -> Result[Optional[User]]:
    return await User.create(
        username=body.username,
        discord_user_id=body.discord_user_id,
        password=body.password,
    )
