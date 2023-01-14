# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
import logging
import time
from typing import Optional

from playwright.async_api import Browser, async_playwright

from config import Config
from engine.browser import screenshot_engine
from engine.request import Request

logger = logging.getLogger(__name__)


class Worker:
    def __init__(self):
        self.queue: asyncio.Queue[Request] = asyncio.Queue()
        self.current_task: Optional[asyncio.Task] = None

    def start(self, loop) -> None:
        logger.info("Starting worker")
        loop.create_task(self._worker())

    def register_request(self, request: Request) -> None:
        logger.info("Added a new task to the queue with type %s", request.request_type.name)
        self.queue.put_nowait(request)

    async def stop(self) -> None:
        logger.info("Shutting down worker")
        while self.queue.qsize() != 0:
            task = await self.queue.get()
            if task.is_stop_code():
                return
            task.waiting_event.set()
            task.future_data.set_exception(Exception("Server is shutting down please try again later"))
            self.queue.task_done()
        if self.current_task is not None:
            self.current_task.cancel()
        await self.queue.put(Request.stop_code())
        await self.queue.join()
        logger.info("Worker shutdown successfully")

    async def _worker(self):
        async with async_playwright() as playwright:
            logger.info("Worker pool started")
            _browser: Optional[Browser] = None
            while True:
                task = await self.queue.get()
                start = time.perf_counter()
                try:
                    if task.is_stop_code():
                        logger.info("Worker shutting down")
                        break
                    task.waiting_event.set()
                    if _browser is None:
                        _browser = await asyncio.wait_for(playwright.chromium.launch(), 20)
                    self.current_task = asyncio.create_task(
                        screenshot_engine(browser=_browser, printer=task.printer, user_lock=task.user_lock)  # type: ignore
                    )
                    await asyncio.wait_for(self.current_task, Config.REQUEST_TIMEOUT + 20)
                    task.future_data.set_result(0)  # type: ignore
                    logger.info(f"Took {time.perf_counter() - start:.2f} to statisfy the request")
                except asyncio.TimeoutError:
                    logger.error("Excepted Timeout Error")
                    task.future_data.set_exception(Exception("request timeout"))
                except Exception as e:
                    logger.error(e, exc_info=True)
                    task.future_data.set_exception(e if str(e) != "" else Exception("something went wrong"))
                    if _browser is not None:
                        logger.debug("Closing browser object")
                        await _browser.close()
                        _browser = None
                finally:
                    if self.queue.empty() or task.is_stop_code():
                        if _browser is not None:
                            logger.debug("Closing browser object")
                            await _browser.close()
                        _browser = None
                    self.current_task = None
                    self.queue.task_done()
