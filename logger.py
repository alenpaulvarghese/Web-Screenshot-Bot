# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(process)d] [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
    datefmt="[%Y-%m-%d %H:%M:%S %z]",
    force=True,
)

logging.getLogger("pyrogram").setLevel("WARNING")
logging.getLogger("websockets").setLevel("WARNING")
logging.getLogger("PIL").setLevel("WARNING")
