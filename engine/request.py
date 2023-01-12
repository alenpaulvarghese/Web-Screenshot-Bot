# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
from enum import Enum
from io import BytesIO
from typing import Optional

from config import Config
from helper.printer import Printer, ScrollMode


class RequestType(Enum):
    REQUEST = 'render'
    STOPCODE = 'stopcode'


class Request:
    def __init__(self, request_type: RequestType, printer: Optional[Printer] = None):
        loop = asyncio.get_running_loop()
        # The link that has to be rendered.
        self.printer = printer
        # used to check if the process is resolved.
        self.future_data: asyncio.Future[BytesIO] = loop.create_future()
        # output type of the render request pdf/png/jpeg
        self.request_type = request_type
        # wait for the webpage to load until this lock is released by the user.
        self.user_lock = asyncio.Event()
        # used to inform user whether a request is in queue or render.
        self.waiting_event = asyncio.Event()

    def register_user_lock(self) -> asyncio.Event:
        """Function to release user lock after a specified time."""
        delay = Config.REQUEST_TIMEOUT if self.printer.scroll_control == ScrollMode.MANUAL else 2
        asyncio.get_running_loop().call_later(delay=delay, callback=self.user_lock.set)
        return self.user_lock

    def is_stop_code(self) -> bool:
        """Check if a instance is Stop Code."""
        return self.request_type == RequestType.STOPCODE

    @staticmethod
    def from_printer(printer: Printer) -> 'Request':
        """Create request instance from printer."""
        return Request(request_type=RequestType.REQUEST, printer=printer)

    @staticmethod
    def stop_code() -> "Request":
        """Create stop code instance."""
        return Request(request_type=RequestType.STOPCODE)
