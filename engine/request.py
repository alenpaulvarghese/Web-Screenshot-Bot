# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from typing import NamedTuple
from asyncio import Future
from helper import Printer


class Request(NamedTuple):
    printer: Printer
    fut_data: Future


class StopCode:
    ...
