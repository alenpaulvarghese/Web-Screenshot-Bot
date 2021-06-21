# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from typing import Dict, Optional, Tuple
from engine import Worker, Request
from pyrogram import Client
from logger import logging
from helper import Printer
from config import Config
import asyncio
import signal
import shutil
import os


_LOG = logging.getLogger(__name__)


class WebshotBot(Client):
    def __init__(self):
        super().__init__(
            session_name="webshot-bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins"),
        )
        self.request_cache: Dict[int, asyncio.Event] = {}
        self.worker = Worker()

    def start(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: asyncio.create_task(self.stop()))
        super().start()
        self.worker.start(loop)
        _LOG.info("Client started")
        loop.run_forever()

    async def stop(self):
        await asyncio.gather(self.worker.close(), self.shutdown_cleanup())
        await super().stop()
        _LOG.info("Client Disconnected")
        for task in asyncio.all_tasks():
            if task is not asyncio.current_task():
                task.cancel()
        _LOG.info("Closing Event Loop")
        asyncio.get_running_loop().stop()

    def get_request(self, _id: int) -> Optional[asyncio.Event]:
        return self.request_cache.get(_id)

    def new_request(
        self, printer: Printer, _id: Optional[int] = None
    ) -> Tuple[asyncio.Future, asyncio.Event]:
        future = asyncio.get_event_loop().create_future()
        user_lock = asyncio.Event()
        waiting_event = asyncio.Event()
        asyncio.create_task(
            self.release_user_lock(user_lock, 30 if printer.scroll_control else 2)
        )
        if _id is not None:
            self.request_cache[_id] = user_lock
        request = Request(printer, future, user_lock, waiting_event)
        self.worker.new_task(request)
        return future, waiting_event

    async def shutdown_cleanup(self):
        if Config.LOG_GROUP is not None and os.path.isfile("debug.log"):
            await self.send_document(
                Config.LOG_GROUP, "debug.log", caption="cycling log"
            )
            os.remove("debug.log")
        if os.path.isdir("./FILES"):
            shutil.rmtree("./FILES")

    @staticmethod
    async def release_user_lock(event: asyncio.Event, _time: float):
        await asyncio.sleep(_time)
        event.set()
