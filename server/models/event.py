from __future__ import annotations

import asyncio
from typing import Annotated, List, Optional, Self

import asyncpg  # type: ignore
import pydantic

from .result import Result
from .snowflake import Snowflake
from .device import Device
from ..codes import DATABASE_FAILURE, DEVICE_NOT_FOUND, INCORRECT_CREDENTIALS
from ..state import STATE


__all__ = ("Event",)


class Event(Snowflake):
    """Represents a device event"""

    category: Annotated[int, pydantic.Field(description="The event category")]
    accel_x: Annotated[Optional[float], pydantic.Field(description="The X acceleration value")]
    accel_y: Annotated[Optional[float], pydantic.Field(description="The Y acceleration value")]
    accel_z: Annotated[Optional[float], pydantic.Field(description="The Z acceleration value")]
    gyro_x: Annotated[Optional[float], pydantic.Field(description="The X gyroscope value")]
    gyro_y: Annotated[Optional[float], pydantic.Field(description="The Y gyroscope value")]
    gyro_z: Annotated[Optional[float], pydantic.Field(description="The Z gyroscope value")]
    heart_rate_bpm: Annotated[Optional[int], pydantic.Field(description="The heart rate in BPM")]
    spo2: Annotated[Optional[int], pydantic.Field(description="The blood oxygen level (SpO2) percentage")]
    latitude: Annotated[Optional[float], pydantic.Field(description="The GPS latitude")]
    longitude: Annotated[Optional[float], pydantic.Field(description="The GPS longitude")]
    neo6m_altitude_meter: Annotated[Optional[float], pydantic.Field(description="The GPS altitude in meters")]
    pressure_pa: Annotated[Optional[float], pydantic.Field(description="The pressure in pascals")]
    bmp280_altitude_meter: Annotated[Optional[float], pydantic.Field(description="The barometric altitude in meters")]
    device: Annotated[Device, pydantic.Field(description="The device that generated the event")]

    @classmethod
    def from_row(cls, row: asyncpg.Record) -> Self:
        return cls(
            id=row["event_id"],
            category=row["event_category"],
            accel_x=row["event_accel_x"],
            accel_y=row["event_accel_y"],
            accel_z=row["event_accel_z"],
            gyro_x=row["event_gyro_x"],
            gyro_y=row["event_gyro_y"],
            gyro_z=row["event_gyro_z"],
            heart_rate_bpm=row["event_heart_rate_bpm"],
            spo2=row["event_spo2"],
            latitude=row["event_latitude"],
            longitude=row["event_longitude"],
            neo6m_altitude_meter=row["event_neo6m_altitude_meter"],
            pressure_pa=row["event_pressure_pa"],
            bmp280_altitude_meter=row["event_bmp280_altitude_meter"],
            device=Device.from_row(row),
        )

    @classmethod
    async def get_for_device(cls, *, device_id: int, user_id: int) -> Result[List[Self]]:
        pool = await STATE.database.get_pool()
        if pool is None:
            return Result(code=DATABASE_FAILURE, data=[])

        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM view_events WHERE device_id = $1 AND user_id = $2", device_id, user_id)
            events = [cls.from_row(row) for row in rows]
            return Result(data=events)

    @classmethod
    async def create(
        cls,
        *,
        category: int,
        accel_x: Optional[float],
        accel_y: Optional[float],
        accel_z: Optional[float],
        gyro_x: Optional[float],
        gyro_y: Optional[float],
        gyro_z: Optional[float],
        heart_rate_bpm: Optional[int],
        spo2: Optional[int],
        latitude: Optional[float],
        longitude: Optional[float],
        neo6m_altitude_meter: Optional[float],
        pressure_pa: Optional[float],
        bmp280_altitude_meter: Optional[float],
        device_id: int,
        device_token: str
    ) -> Result[Optional[Self]]:
        pool = await STATE.database.get_pool()
        if pool is None:
            return Result(code=DATABASE_FAILURE, data=None)

        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM view_devices WHERE device_id = $1", device_id)
            if row is None:
                return Result(code=DEVICE_NOT_FOUND, data=None)

            device = Device.from_row(row)
            try:
                STATE.hasher.verify(device.hashed_token, device_token)

            except Exception:
                return Result(code=INCORRECT_CREDENTIALS, data=None)

            async def _rehash_task() -> None:
                if STATE.hasher.check_needs_rehash(device.hashed_token):
                    new_hashed = STATE.hasher.hash(device_token)
                    async with pool.acquire() as conn:
                        await conn.execute(
                            "UPDATE Devices SET hashed_token = $1 WHERE id = $2",
                            new_hashed,
                            device.id,
                        )

            asyncio.create_task(_rehash_task())
            row = await conn.fetchrow(
                "SELECT * FROM create_event("
                "    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,"
                "    $11, $12, $13, $14, $15"
                ")",
                category,
                accel_x,
                accel_y,
                accel_z,
                gyro_x,
                gyro_y,
                gyro_z,
                heart_rate_bpm,
                spo2,
                latitude,
                longitude,
                neo6m_altitude_meter,
                pressure_pa,
                bmp280_altitude_meter,
                device_id,
            )
            return Result(data=cls.from_row(row))
