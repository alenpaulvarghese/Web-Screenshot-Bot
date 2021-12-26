# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
import logging
from http.client import BadStatusLine, ResponseNotReady

from config import Config
from helper import Printer, inject_reader
from helper.images import draw_statics
from pyppeteer import errors, launch
from pyppeteer.browser import Browser

_LOG = logging.getLogger(__name__)


async def launch_browser(retry=False) -> Browser:
    """Function used to launch chromium browser."""
    try:
        _LOG.info("Launching browser")
        browser = await launch(
            headless=True,
            logLevel=50,
            executablePath=Config.EXEC_PATH,
            handleSIGINT=False,
            args=[
                "--no-sandbox",
                "--single-process",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--no-zygote",
            ],
        )
        return browser
    except BadStatusLine as e:
        if not retry:
            _LOG.error("Launching browser failed due to %s, retrying...", e)
            await asyncio.sleep(1.5)
            return await launch_browser(True)
        elif retry:
            _LOG.error("Launching browser failed due to %s, exiting...", e)


async def screenshot_engine(
    browser: Browser, printer: Printer, user_lock: asyncio.Event
):
    page = await browser.newPage()
    await page.setViewport(printer.resolution)
    try:
        await page.goto(printer.link, dict(timeout=60000))
        inject_str = await asyncio.get_event_loop().run_in_executor(None, inject_reader)
        title, _ = await asyncio.gather(
            page.title(), page.evaluate(inject_str, force_expr=True)
        )
        printer.slugify(title[:14])
        if printer.type == "statics":
            (height, width), metrics = await asyncio.gather(
                page.evaluate("[getHeight(), getWidth()]"),
                page.metrics(),
            )
            page_data = dict(Height=height, Width=width)
            page_data.update(metrics)
            byteio_file = await asyncio.get_running_loop().run_in_executor(
                None, draw_statics, title[:25], page_data
            )
            printer.set_location(byteio_file)
        else:
            if printer.scroll_control != "no" and printer.fullpage is True:
                if printer.scroll_control == "auto":
                    await page.evaluate("scroll(getHeight());")
                elif printer.scroll_control == "manual":
                    asyncio.create_task(page.evaluate("progressiveScroll();"))
                    await user_lock.wait()
                    await page.evaluate("cancelScroll()")
            if printer.type == "pdf":
                await page.pdf(printer.print_arguments, path=printer.file)
            else:
                await page.screenshot(printer.print_arguments, path=printer.file)
    except errors.PageError:
        raise ResponseNotReady("This is not a valid link 🤔")
    except asyncio.CancelledError:
        raise ResponseNotReady("server got interuppted, please try again later")
    finally:
        await page.close()
