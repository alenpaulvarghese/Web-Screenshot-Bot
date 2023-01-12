# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import io
import shutil
from enum import Enum
from pathlib import Path
from re import sub
from typing import TypedDict, Union

from pyrogram.types import Message


class RenderType(Enum):
    PDF = "pdf"
    PNG = "png"
    JPEG = "jpeg"

    @staticmethod
    def is_image(render_type: "RenderType") -> bool:
        return render_type in (RenderType.JPEG, RenderType.PNG)


class ScrollMode(Enum):
    OFF = "no"
    MANUAL = "manual"
    AUTO = "auto"


class CacheData(TypedDict):
    split: bool
    fullpage: bool
    resolution: str
    render_type: RenderType
    scroll_control: ScrollMode


Location = Union[Path, io.BytesIO]


class Printer(object):
    def __init__(self, render_type: RenderType, link: str):
        self.resolution = {"width": 800, "height": 600}
        self.link = link
        self.split = False
        self.fullpage = True
        self.type = render_type
        self.scroll_control = ScrollMode.OFF
        self.location: Location = Path("./FILES")
        self.name = "@Webs-Screenshot"

    def _get_logstr(self, _id: int, name: str) -> str:
        """String containing informations for logging."""
        res = "{width}x{height}".format_map(self.resolution)
        return (
            f"|- [{name}](tg://user?id={_id})\n"
            f"|- Format - > `{self.type}`\n|- Resolution - > `{res}`\n"
            f"|- Page - > `{self.fullpage}`\n|- ScrollControl - > `{self.scroll_control}`\n"
            f"|- Split - > `{self.split}`\n|- `{self.link}`"
        )

    def cache_dict(self) -> CacheData:
        return CacheData(
            render_type=self.type,
            split=self.split,
            fullpage=self.fullpage,
            scroll_control=self.scroll_control,
            resolution="{width}x{height}".format_map(self.resolution),
        )

    def get_render_arguments(self) -> dict:
        """Dict containing arguments used to feed browser."""
        if self.type == RenderType.PDF:
            arguments_for_pdf = {
                "display_header_footer": True,
                "margin": {"bottom": "70", "left": "25", "right": "35", "top": "40"},
                "print_background": True,
            }
            if self.resolution["width"] == 800:
                arguments_for_pdf["format"] = "Letter"
            else:
                arguments_for_pdf.update(self.resolution)
            if not self.fullpage:
                arguments_for_pdf["page_ranges"] = "1-2"
            return arguments_for_pdf
        if RenderType.is_image(self.type):
            arguments_for_image = {"type": self.type.value, "omit_background": False}
            if self.fullpage:
                arguments_for_image["full_page"] = True
            return arguments_for_image
        return {}

    @property
    def file(self) -> Location:
        """Contains the path to the file or in-memory object."""
        if isinstance(self.location, Path):
            return self.location / f"{self.name}.{self.type.value}"
        return self.location

    def cleanup(self):
        """Cleanup rendered files."""
        if isinstance(self.location, Path):
            try:
                shutil.rmtree(self.location)
            except FileNotFoundError:
                pass
        elif isinstance(self.location, io.BytesIO):
            self.location.close()

    def set_filename(self, text: str):
        """Function that sets slugified filename."""
        # https://stackoverflow.com/a/295466/13033981
        text = sub(r"[^\w\s-]", "", text.lower())
        self.name = sub(r"[-\s]+", "-", text).strip("-_")

    def allocate_folder(self, chat_id: int, message_id: int):
        """Allocate folder based on chat_id and message_id."""
        location = Path(self.location, str(chat_id), str(message_id))  # type: ignore
        location.mkdir(parents=True, exist_ok=True)
        self.set_location(location)

    def set_location(self, loc: Location):
        """Set value for location attribute."""
        self.location = loc

    @staticmethod
    def from_message(message: Message) -> "Printer":
        """Function that parse render settings from message."""
        split, resolution, scroll_control = False, "", ScrollMode.OFF
        for settings in message.reply_markup.inline_keyboard:
            text = settings[0].text
            if "Format" in text:
                if "PDF" in text:
                    _format = RenderType.PDF
                else:
                    _format = RenderType.PNG if "PNG" in text else RenderType.JPEG
            if "Page" in text:
                page_value = "Full" in text
            if "Scroll" in text:
                if "Auto" in text:
                    scroll_control = ScrollMode.AUTO
                elif "Manual" in text:
                    scroll_control = ScrollMode.MANUAL
            if "Split" in text:
                split = "Yes" in text
            if "resolution" in text:
                resolution = text
        printer = Printer(_format, message.reply_to_message.text)  # type: ignore
        printer.scroll_control = scroll_control  # type: ignore
        printer.fullpage = page_value
        printer.split = split
        if resolution:
            if "1280" in resolution:
                printer.resolution = {"width": 1280, "height": 720}
            elif "2560" in resolution:
                printer.resolution = {"width": 2560, "height": 1440}
            elif "1080" in resolution:
                printer.resolution = {"width": 1080, "height": 1920}
        return printer
