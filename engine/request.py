# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from asyncio import Future, Event
from typing import NamedTuple
from helper import Printer


class Request(NamedTuple):
    printer: Printer
    future_data: Future
    user_lock: Event


class StopCode:
    ...
