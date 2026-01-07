from __future__ import annotations

from typing import Annotated, List, Optional

import pydantic
from fastapi import APIRouter, Depends

from .root import get_current_user
from ..models import Device, Event, Result, User


__all__ = ("devices_router",)
devices_router = APIRouter(prefix="/devices", tags=["devices"])


@devices_router.get("/", summary="List all devices of the current user")
async def get(
    user: Annotated[User, Depends(get_current_user)],
) -> Result[List[Device]]:
    return await Device.get_all(user_id=user.id)


@devices_router.get("/{id}", summary="Query a device by ID")
async def get_id(id: int) -> Result[Optional[Device]]:
    return await Device.get(id=id)


class _PostBody(pydantic.BaseModel):
    name: str
    token: str


@devices_router.post("/", summary="Create a new device")
async def post(
    user: Annotated[User, Depends(get_current_user)],
    body: _PostBody,
) -> Result[Optional[Device]]:
    return await Device.create(name=body.name, token=body.token, user_id=user.id)


@devices_router.get("/{id}/events", summary="List all events for a device", tags=["events"])
async def get_device_events(
    user: Annotated[User, Depends(get_current_user)],
    id: int,
) -> Result[List[Event]]:
    return await Event.get_for_device(device_id=id, user_id=user.id)
