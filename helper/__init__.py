# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.types import InputMediaPhoto
from .images import split_image, draw_statics  # noqa
from .printer import Printer  # noqa
from typing import Iterator, List
import asyncio


async def settings_parser(link: str, inline_keyboard: list) -> Printer:
    # starting to recognize settings
    split, resolution = False, ""
    for settings in inline_keyboard:
        text = settings[0].text
        if "Format" in text:
            if "PDF" in text:
                _format = "pdf"
            else:
                _format = "png" if "PNG" in text else "jpeg"
        if "Page" in text:
            page_value = True if "Full" in text else False
        if "Split" in text:
            split = True if "Yes" in text else False
        if "resolution" in text:
            resolution = text
        await asyncio.sleep(0.00001)
    printer = Printer(_format, link)
    if resolution:
        if "1280" in resolution:
            printer.resolution = {"width": 1280, "height": 720}
        elif "2560" in resolution:
            printer.resolution = {"width": 2560, "height": 1440}
        elif "640" in resolution:
            printer.resolution = {"width": 640, "height": 480}
    if not page_value:
        printer.fullpage = False
    if split:
        printer.split = True
    return printer


def mediagroup_gen(loc: List[str]) -> Iterator[List[InputMediaPhoto]]:
    media_group = [
        InputMediaPhoto(image, str(count)) for count, image in enumerate(loc, start=1)
    ]
    for i in range(0, len(media_group), 10):
        yield media_group[i : i + 10]  # noqa: E203
