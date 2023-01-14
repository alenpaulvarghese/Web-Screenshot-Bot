# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio
import logging
from http.client import ResponseNotReady

from playwright.async_api import Browser, Error

from helper import read_driver_file
from helper.printer import Printer, RenderType, ScrollMode

logger = logging.getLogger(__name__)


async def screenshot_engine(browser: Browser, printer: Printer, user_lock: asyncio.Event):
    page = await browser.new_page(viewport=printer.viewport)  # type: ignore
    try:
        await page.goto(url=printer.link, timeout=60000.0)
        driver_file, title = await asyncio.gather(read_driver_file(), page.title())
        printer.set_filename(title[:14])
        if printer.scroll_control != ScrollMode.OFF and printer.fullpage is True:
            if printer.scroll_control == ScrollMode.AUTO:
                await page.evaluate(f"{driver_file};scroll(getHeight());")
            elif printer.scroll_control == ScrollMode.MANUAL:
                _, pending = await asyncio.wait(
                    fs=(page.evaluate(f"{driver_file};progressiveScroll();"), user_lock.wait()),
                    return_when=asyncio.FIRST_COMPLETED,
                )
                pending.pop().cancel()
        if printer.type == RenderType.PDF:
            await page.pdf(**printer.get_render_arguments())
        else:
            await page.screenshot(**printer.get_render_arguments())
    except asyncio.CancelledError as e:
        raise ResponseNotReady("server got interuppted, please try again later") from e
    finally:
        await page.close()
