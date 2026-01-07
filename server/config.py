from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from yarl import URL


__all__ = ()


ROOT = Path(__file__).parent.parent.resolve()
SNOWFLAKE_EPOCH = datetime(2020, 1, 1, 0, 0, 0, 0, tzinfo=timezone.utc)
JWT_SECRET_KEY = ROOT.joinpath("secrets", "jwt.pem").read_text(encoding="utf-8")
JWT_EXPIRATION_SECONDS = 900
DISCORD_API_URL = URL("https://discord.com/api/v10")

POSTGRES_DB = os.getenv("POSTGRES_DB", "default")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DISCORD_BOT_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
