import logging


logging.basicConfig(
    level="WARNING",
    format="%(asctime)s - %(name)s - [ %(message)s ]",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()],
)
