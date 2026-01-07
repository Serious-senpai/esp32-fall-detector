from __future__ import annotations

from datetime import datetime, timedelta
from typing import Annotated

import pydantic

from ..config import SNOWFLAKE_EPOCH


__all__ = ("Snowflake",)


class Snowflake(pydantic.BaseModel):
    """Base class for all snowflake models"""

    id: Annotated[int, pydantic.Field(description="The snowflake ID")]

    @property
    def created_at(self) -> datetime:
        """The creation time of the snowflake ID"""
        milliseconds = self.id >> 12
        return SNOWFLAKE_EPOCH + timedelta(milliseconds=milliseconds)
