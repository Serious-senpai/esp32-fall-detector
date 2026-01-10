from __future__ import annotations

from typing import Optional

import pydantic
from fastapi import APIRouter

from ..category import FALL_DETECTED
from ..models import Embed, EmbedField, EmbedFooter, EmbedThumbnail, Event, Result
from ..state import STATE


__all__ = ("events_router",)
events_router = APIRouter(prefix="/api/events", tags=["events"])


class _PostBody(pydantic.BaseModel):
    category: int
    accel_x: Optional[float] = None
    accel_y: Optional[float] = None
    accel_z: Optional[float] = None
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    heart_rate_bpm: Optional[int] = None
    spo2: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    neo6m_altitude_meter: Optional[float] = None
    pressure_pa: Optional[float] = None
    bmp280_altitude_meter: Optional[float] = None
    device_id: int
    device_token: str


@events_router.post("/", summary="Upload a new event from a device")
async def post(body: _PostBody) -> Result[Optional[Event]]:
    event = await Event.create(
        category=body.category,
        accel_x=body.accel_x,
        accel_y=body.accel_y,
        accel_z=body.accel_z,
        gyro_x=body.gyro_x,
        gyro_y=body.gyro_y,
        gyro_z=body.gyro_z,
        heart_rate_bpm=body.heart_rate_bpm,
        spo2=body.spo2,
        latitude=body.latitude,
        longitude=body.longitude,
        neo6m_altitude_meter=body.neo6m_altitude_meter,
        pressure_pa=body.pressure_pa,
        bmp280_altitude_meter=body.bmp280_altitude_meter,
        device_id=body.device_id,
        device_token=body.device_token,
    )

    if event.data is not None and event.data.category in (FALL_DETECTED,):
        e = event.data
        fields = [
            EmbedField(name="Category", value=str(e.category)),
        ]
        if e.accel_x is not None and e.accel_y is not None and e.accel_z is not None:
            fields.append(EmbedField(name="Acceleration (g)", value=f"{e.accel_x:.2f}, {e.accel_y:.2f}, {e.accel_z:.2f}", inline=True))
        if e.gyro_x is not None and e.gyro_y is not None and e.gyro_z is not None:
            fields.append(EmbedField(name="Gyroscope (rad/s)", value=f"{e.gyro_x:.2f}, {e.gyro_y:.2f}, {e.gyro_z:.2f}", inline=True))
        if e.heart_rate_bpm is not None:
            fields.append(EmbedField(name="Heart rate", value=f"{e.heart_rate_bpm} BPM", inline=True))
        if e.spo2 is not None:
            fields.append(EmbedField(name="SpO2", value=f"{e.spo2}%", inline=True))
        if e.latitude is not None and e.longitude is not None:
            url = f"https://www.google.com/maps?q={e.latitude},{e.longitude}"
            fields.append(EmbedField(name="Location", value=f"[Google Maps]({url})", inline=True))
        if e.neo6m_altitude_meter is not None:
            fields.append(EmbedField(name="NEO-6M altitude", value=f"{e.neo6m_altitude_meter:.2f} m", inline=True))
        if e.pressure_pa is not None:
            fields.append(EmbedField(name="Pressure", value=f"{e.pressure_pa:.2f} Pa", inline=True))
        if e.bmp280_altitude_meter is not None:
            fields.append(EmbedField(name="BMP280 altitude", value=f"{e.bmp280_altitude_meter:.2f} m", inline=True))

        embeds = [
            Embed(
                title=e.device.name,
                timestamp=e.created_at,
                color=0x2ecc71,
                footer=EmbedFooter(
                    text=f"Event ID: {e.id}",
                ),
                thumbnail=None if STATE.discord_avatar_url is None else EmbedThumbnail(
                    url=STATE.discord_avatar_url,
                ),
                fields=fields,
            ),
        ]
        await e.device.user.send(
            content="A new sensor event has been detected.",
            embeds=embeds,
        )

    return event
