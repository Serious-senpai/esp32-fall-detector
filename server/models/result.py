from __future__ import annotations

from typing import Annotated, Generic, TypeVar

import pydantic

from ..codes import SUCCESS


__all__ = ("Result",)
_SerializableT = TypeVar("_SerializableT")


class Result(pydantic.BaseModel, Generic[_SerializableT]):
    """Response model for all API results"""

    code: Annotated[int, pydantic.Field("The result code of the operation")] = SUCCESS
    data: Annotated[_SerializableT, pydantic.Field(description="The result data of the operation")]
