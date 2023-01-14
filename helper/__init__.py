# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
from pathlib import Path
from typing import Iterator, List

from pyrogram.types import InputMediaPhoto


def mediagroup_gen(loc: List[Path]) -> Iterator[List[InputMediaPhoto]]:
    """Generator function that yields 10 InputMediaPhoto at a time."""
    media_group = [InputMediaPhoto(str(image), str(count)) for count, image in enumerate(loc, start=1)]
    for i in range(0, len(media_group), 10):
        yield media_group[i : i + 10]  # noqa: E203


async def read_driver_file() -> str:
    return await asyncio.get_event_loop().run_in_executor(
        executor=None,
        func=_inject_reader,
    )


def _inject_reader() -> str:
    """Function to read string from file."""
    r_string = ""
    with open(Path("assets", "inject.js")) as f:
        r_string = f.read()
    return r_string
