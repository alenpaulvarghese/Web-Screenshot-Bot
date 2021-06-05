# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from engine.browser import launch_browser, screenshot_engine
from engine.request import Request, StopCode
from pyppeteer.browser import Browser
from typing import Optional
import logging
import asyncio
import time

_LOG = logging.getLogger(__name__)


class Worker(object):
    def __init__(self):
        self.queue: asyncio.Queue[Request] = asyncio.Queue()

    def start(self, loop) -> None:
        loop.create_task(self._worker())

    def new_task(self, task: Request) -> None:
        self.queue.put_nowait(task)

    async def _worker(self) -> None:
        _LOG.info("Worker pool started")
        _browser: Optional[Browser] = None
        while True:
            task = await self.queue.get()
            start = time.perf_counter()
            try:
                if isinstance(task, StopCode):
                    _LOG.info("Worker shutting down")
                    break
                if _browser is None:
                    _browser = await launch_browser()
                await screenshot_engine(_browser, task.printer)  # type: ignore
                task.fut_data.set_result(0)
                _LOG.info(
                    "Took {:.2f} to statisfy the request".format(
                        time.perf_counter() - start
                    )
                )
            except Exception as e:
                _LOG.error("Excepted %s", e)
                task.fut_data.set_exception(e)
                if _browser is not None:
                    await _browser.close()
                    _browser = None
            finally:
                if self.queue.empty() or isinstance(task, StopCode):
                    if _browser is not None:
                        _LOG.info("Closing browser object")
                        await _browser.close()
                    _browser = None
                self.queue.task_done()
