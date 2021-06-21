# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from typing import Optional, Union, Literal
from re import sub
import shutil
import io
import os

_LOC = Union[str, io.BytesIO]


class Printer(object):
    def __init__(self, _type: Literal["pdf", "png", "jpeg", "statics"], _link: str):
        self.resolution = {"width": 800, "height": 600}
        self.type = _type
        self.link = _link
        self.split = False
        self.fullpage = True
        self.scroll_control: Optional[bool] = False
        self.location: _LOC = "./FILES"
        self.name = "@Webs-Screenshot"

    def _get_logstr(self, _id: int, name: str) -> str:
        res = "{width}x{height}".format_map(self.resolution)
        return (
            f"|- [{name}](tg://user?id={_id})\n|- Resolution - > `{res}`\n"
            f"|- Page - > `{self.fullpage}`\n|- ScrollControl - > `{self.scroll_control}`\n"
            f"|- Split - > `{self.split}`\n|- `{self.link}`"
        )

    @property
    def arguments_to_print(self) -> dict:
        if self.type == "pdf":
            arguments_for_pdf = {
                "displayHeaderFooter": True,
                "margin": {"bottom": 70, "left": 25, "right": 35, "top": 40},
                "printBackground": True,
            }
            if self.resolution["width"] == 800:
                arguments_for_pdf["format"] = "Letter"
            else:
                arguments_for_pdf = {**arguments_for_pdf, **self.resolution}
            if not self.fullpage:
                arguments_for_pdf["pageRanges"] = "1-2"
            return arguments_for_pdf
        elif self.type == "png" or self.type == "jpeg":
            arguments_for_image = {"type": self.type, "omitBackground": False}
            if self.fullpage:
                arguments_for_image["fullPage"] = True
            return arguments_for_image
        return {}

    @property
    def file(self) -> _LOC:
        if isinstance(self.location, str):
            return self.location + self.name + "." + self.type
        else:
            return self.location

    def cleanup(self) -> None:
        """Cleanup rendered files."""
        if isinstance(self.location, str):
            try:
                shutil.rmtree(self.location)
            except FileNotFoundError:
                pass
        elif isinstance(self.location, io.BytesIO):
            self.location.close()

    def slugify(self, text: str):
        """Function to convert string to a valid file-name."""
        # https://stackoverflow.com/a/295466/13033981
        text = sub(r"[^\w\s-]", "", text.lower())
        self.name = sub(r"[-\s]+", "-", text).strip("-_")

    def allocate_folder(self, chat_id: int, message_id: int):
        """Allocate folder based on chat_id and message_id."""
        if not os.path.isdir("./FILES"):
            os.mkdir("./FILES")
        location = f"./FILES/{str(chat_id)}/{str(message_id)}/"
        if not os.path.isdir(location):
            os.makedirs(location)
        self.set_location(location)

    def set_location(self, loc: _LOC) -> None:
        """Set value for location attribute."""
        self.location = loc
