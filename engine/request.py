# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from asyncio import Future, Event
from typing import NamedTuple
from helper import Printer


class Request(NamedTuple):
    # printer contains the information for rendering
    printer: Printer
    # used to check if the process is resolved
    future_data: Future
    # used to wait the loading utill user prompted otherwise
    user_lock: Event
    # used to inform user whether a request is in queue or render
    waiting_event: Event


# dummy class used to stop the worker
class StopCode:
    ...
