from __future__ import annotations

from typing import Annotated, Literal

import pydantic
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..crypt import decode_jwt, encode_jwt
from ..models import Result, User


__all__ = ("root_router",)
root_router = APIRouter(prefix="/api")
OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="login")
INVALID_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Invalid credentials",
)


@root_router.get("/", summary="Root endpoint for health checking")
async def get_root() -> Result[None]:
    return Result(data=None)


class _Token(pydantic.BaseModel):
    access_token: str
    token_type: Literal["bearer"]


@root_router.post(
    "/login",
    summary="Login as a user",
)
async def post_login(body: Annotated[OAuth2PasswordRequestForm, Depends()]) -> _Token:
    user = await User.login(username=body.username, password=body.password)
    inner = user.data
    if inner is None:
        raise INVALID_CREDENTIALS

    token = encode_jwt(str(inner.id))
    return _Token(access_token=token, token_type="bearer")


async def get_current_user(token: Annotated[str, Depends(OAUTH2_SCHEME)]) -> User:
    user_id = decode_jwt(token)
    if user_id is None or not user_id.isdecimal():
        raise INVALID_CREDENTIALS

    user = await User.get(id=int(user_id))
    inner = user.data
    if inner is None:
        raise INVALID_CREDENTIALS

    return inner


@root_router.get("/@me", summary="Get the current authenticated user")
async def get_me(user: Annotated[User, Depends(get_current_user)]) -> Result[User]:
    return Result(data=user)
