import os
from contextlib import suppress
from typing import Optional

from dotenv import load_dotenv


def init_log() -> Optional[int]:
    if (log_group := os.environ.get("LOG_GROUP")) is not None:
        with suppress(ValueError):
            return int(log_group)
    return None


if os.path.isfile("config.env"):
    load_dotenv("config.env")


class Config:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    API_ID = int(os.environ["API_ID"])
    API_HASH = os.environ["API_HASH"]
    EXEC_PATH = os.environ.get("GOOGLE_CHROME_SHIM", None)
    # OPTIONAL
    LOG_GROUP = init_log()
    SUPPORT_GROUP_LINK = os.environ.get("SUPPORT_GROUP", "https://t.me/bytessupport")
