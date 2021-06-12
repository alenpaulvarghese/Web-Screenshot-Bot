# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from http.client import BadStatusLine, ResponseNotReady
from helper.images import draw_statics
from pyppeteer.browser import Browser
from pyppeteer import launch, errors
from helper import Printer
from config import Config
import logging
import asyncio

_LOG = logging.getLogger(__name__)


async def launch_browser(retry=False) -> Browser:
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
        title = await page.title()
        printer.slugify(title[:14])
        if printer.render_control is not None:
            control = asyncio.create_task(
                page.evaluate(
                    """
                    async function scroll(){
                        let height = Math.max(
                            document.body.scrollHeight,
                            document.body.offsetHeight,
                            document.documentElement.clientHeight,
                            document.documentElement.scrollHeight,
                            document.documentElement.offsetHeight);
                        for (let i=0; i <= height; i += 10) {
                            window.scrollTo(0, i);
                            await new Promise(r => setTimeout(r, 1));
                            }
                    };
                    scroll();
                    """,
                    force_expr=True,
                )
            )
            if printer.render_control is False:
                await control
            await user_lock.wait()
            control.cancel()
        if printer.type == "pdf":
            await page.pdf(printer.arguments_to_print, path=printer.file)
        elif printer.type == "statics":
            height, width, metrics = await asyncio.gather(
                page.evaluate(
                    "Math.max(document.body.scrollHeight, document.body.offsetHeight, "
                    "document.documentElement.clientHeight, document.documentElement.scrollHeight, "
                    "document.documentElement.offsetHeight);"
                ),
                page.evaluate(
                    "Math.max(document.body.scrollWidth, document.body.offsetWidth, "
                    "document.documentElement.clientWidth, document.documentElement.scrollWidth, "
                    "document.documentElement.offsetWidth);"
                ),
                page.metrics(),
            )
            page_data = dict(Height=height, Width=width)
            page_data.update(metrics)
            byteio_file = await asyncio.get_running_loop().run_in_executor(
                None, draw_statics, title[:25], page_data
            )
            printer.set_location(byteio_file)
        else:
            await page.screenshot(printer.arguments_to_print, path=printer.file)
    except errors.PageError:
        raise ResponseNotReady("This is not a valid link 🤔")
    finally:
        await page.close()
