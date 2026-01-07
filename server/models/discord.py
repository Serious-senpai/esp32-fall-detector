from __future__ import annotations

from datetime import datetime
from typing import Annotated, List, Literal, Optional

import pydantic
from pydantic import PlainSerializer


__all__ = ("Embed", "EmbedFooter", "EmbedThumbnail", "EmbedField")


class Embed(pydantic.BaseModel):
    title: Optional[str] = None
    type: Literal["rich"] = "rich"
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[Annotated[datetime, PlainSerializer(datetime.isoformat, return_type=str)]] = None
    color: Optional[int] = None
    footer: Optional[EmbedFooter] = None
    thumbnail: Optional[EmbedThumbnail] = None
    fields: Optional[List[EmbedField]] = None


class EmbedFooter(pydantic.BaseModel):
    text: str
    icon_url: Optional[str] = None
    proxy_icon_url: Optional[str] = None


class EmbedThumbnail(pydantic.BaseModel):
    url: str
    proxy_url: Optional[str] = None
    height: Optional[int] = None
    width: Optional[int] = None


class EmbedField(pydantic.BaseModel):
    name: str
    value: str
    inline: Optional[bool] = None
