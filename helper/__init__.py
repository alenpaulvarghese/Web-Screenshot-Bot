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
        if "Scroll" in text:
            if "No" in text:
                scroll_control = None
            elif "Auto" in text:
                scroll_control = False
            elif "Manual" in text:
                scroll_control = True
        if "Split" in text:
            split = True if "Yes" in text else False
        if "resolution" in text:
            resolution = text
        await asyncio.sleep(0.00001)
    printer = Printer(_format, link)  # type: ignore
    printer.scroll_control = scroll_control
    printer.fullpage = page_value
    printer.split = split
    if resolution:
        if "1280" in resolution:
            printer.resolution = {"width": 1280, "height": 720}
        elif "2560" in resolution:
            printer.resolution = {"width": 2560, "height": 1440}
        elif "640" in resolution:
            printer.resolution = {"width": 640, "height": 480}
    return printer


def mediagroup_gen(loc: List[str]) -> Iterator[List[InputMediaPhoto]]:
    media_group = [
        InputMediaPhoto(image, str(count)) for count, image in enumerate(loc, start=1)
    ]
    for i in range(0, len(media_group), 10):
        yield media_group[i : i + 10]  # noqa: E203
