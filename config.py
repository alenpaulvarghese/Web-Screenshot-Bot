import os


def init_log() -> int:
    return (
        int(log_group)  # type: ignore
        if (log_group := os.environ.get("LOG_GROUP")) is not None
        else None
    )


class Config:
    BOT_TOKEN = os.environ["BOT_TOKEN"]
    API_ID = int(os.environ["API_ID"])
    API_HASH = os.environ["API_HASH"]
    LOG_GROUP = init_log()