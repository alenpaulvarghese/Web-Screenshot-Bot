# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
import os
import shutil
import signal
from typing import Dict, Optional, Tuple

from cachetools import LRUCache
from pyrogram.client import Client

from config import Config
from engine.request import Request
from engine.worker import Worker
from helper.printer import CacheData, Printer
from logger import logging

_LOG = logging.getLogger(__name__)


class WebshotBot(Client):
    def __init__(self):
        super().__init__(
            name="webshot-bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins"),
        )
        self.request_cache: Dict[int, asyncio.Event] = {}
        self.settings_cache: LRUCache[int, CacheData] = LRUCache(8)
        self.worker = Worker()

    def start(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        super(WebshotBot, self).start()
        self.worker.start(loop)
        _LOG.info("Client started")
        loop.run_forever()

    async def stop(self):
        await asyncio.gather(self.worker.stop(), self.shutdown_cleanup())
        await super(WebshotBot, self).stop()
        _LOG.info("Client Disconnected")
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
        _LOG.info("Closing Event Loop")
        asyncio.get_running_loop().stop()

    def get_request(self, _id: int) -> Optional[asyncio.Event]:
        return self.request_cache.get(_id)

    def get_settings_cache(self, _id: int) -> Optional[CacheData]:
        return self.settings_cache.get(_id)

    def new_request(self, printer: Printer, _id: Optional[int] = None) -> Tuple[asyncio.Future, asyncio.Event]:
        request = Request.from_printer(printer)
        user_lock = request.register_user_lock()
        if _id is not None:
            self.request_cache[_id] = user_lock
            self.settings_cache[_id] = printer.cache_dict()
        self.worker.register_request(request)
        return request.future_data, request.waiting_event

    async def shutdown_cleanup(self):
        if Config.LOG_GROUP is not None and os.path.isfile("debug.log"):
            await self.send_document(Config.LOG_GROUP, "debug.log", caption="cycling log")
            os.remove("debug.log")
        if os.path.isdir("./FILES"):
            shutil.rmtree("./FILES")

    @staticmethod
    async def release_user_lock(event: asyncio.Event, _time: float):
        await asyncio.sleep(_time)
        event.set()
