from engine import Worker, Request, StopCode
from pyrogram import Client
from logger import logging
from helper import Printer
from creds import my
import asyncio
import signal


_LOG = logging.getLogger(__name__)


class WebshotBot(Client):
    def __init__(self):
        super().__init__(
            session_name="webshot-bot",
            api_id=my.API_ID,
            api_hash=my.API_HASH,
            bot_token=my.BOT_TOKEN,
            plugins=dict(root="plugins"),
        )
        self.worker = Worker()

    def start(self):
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, lambda: self.stop())
        super().start()
        self.worker.start(loop)
        _LOG.info("Client started")

    def stop(self):
        self.worker.new_task(StopCode())

    def new_request(self, printer: Printer) -> asyncio.Future:
        fut = asyncio.get_event_loop().create_future()
        self.worker.new_task(Request(printer, fut))
        return fut
