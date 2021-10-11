# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from .images import split_image, draw_statics  # noqa
from pyrogram.types import InputMediaPhoto
from typing import Iterator, List
from .printer import Printer, _CDICT  # noqa
from pathlib import Path


def mediagroup_gen(loc: List[Path]) -> Iterator[List[InputMediaPhoto]]:
    """Generator function that yields 10 InputMediaPhoto at a time."""
    media_group = [
        InputMediaPhoto(image, str(count)) for count, image in enumerate(loc, start=1)
    ]
    for i in range(0, len(media_group), 10):
        yield media_group[i : i + 10]  # noqa: E203


def inject_reader() -> str:
    """Function to read string from file."""
    r_string = ""
    with open(Path("assets", "inject.js")) as f:
        r_string = f.read()
    return r_string
