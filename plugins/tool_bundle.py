# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from http.client import (
    BadStatusLine,
    ResponseNotReady
)
from pyrogram.types import (
    Message,
    InputMediaPhoto
)
from pyppeteer import (
    launch,
    errors
)
from typing import (
    List,
    Tuple,
    Union
)
from PIL import (
    Image,
    ImageFont,
    ImageDraw
)
from pyppeteer.browser import Browser
from plugins.logger import logging  # pylint:disable=import-error
from pyrogram import Client
from zipfile import ZipFile
from requests import get
from random import randint
import asyncio
import shutil
import math
import io
import os


EXEC_PATH = os.environ.get('GOOGLE_CHROME_SHIM', None)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


class Printer(object):
    def __init__(self, _type: str, _link: str, _pid: int):
        self.resolution = {'width': 800, 'height': 600}
        self.type = _type
        self.link = _link
        self.PID = _pid
        self.fullpage = True
        self.split = False
        self.name = f"@Webs-Screenshot.{self.type}"

    def __str__(self):
        res = f'{self.resolution["width"]}+{self.resolution["height"]}'
        return f'({self.type}|{res}|{self.fullpage})\n```{self.link}```'

    @property
    def arguments_to_print(self) -> dict:
        if self.type == "pdf":
            arguments_for_pdf = {
                'displayHeaderFooter': True,
                'margin': {"bottom": 70, "left": 25, "right": 35, "top": 40},
                "printBackground": True
            }
            if self.resolution['width'] == 800:
                arguments_for_pdf['format'] = "Letter"
            else:
                arguments_for_pdf = {**arguments_for_pdf, **self.resolution}
            if not self.fullpage:
                arguments_for_pdf["pageRanges"] = "1-2"
            return arguments_for_pdf
        elif self.type == "png" or self.type == "jpeg":
            arguments_for_image = {
                'type': self.type, "omitBackground": True}
            if self.fullpage:
                arguments_for_image['fullPage'] = True
            return arguments_for_image


# https://stackoverflow.com/questions/25705773/image-cropping-tool-python
async def split_func(out: io.BytesIO, _format: str) -> List[io.BytesIO]:
    Image.MAX_IMAGE_PIXELS = None
    # https://coderwall.com/p/ovlnwa/use-python-and-pil-to-slice-an-image-vertically
    location_of_image = []
    img = Image.open(out)
    width, height = img.size
    upper, left, count, slice_size = 0, 0, 1, 800
    slices = int(math.ceil(height/slice_size))
    for _ in range(slices):
        # if we are at the end, set the lower bound to be the bottom of the image
        if count == slices:
            lower = height
        else:
            lower = int(count * slice_size)
        bbox = (left, upper, width, lower)
        working_slice = img.crop(bbox)
        upper += slice_size
        # saving = the slice
        if 'jpeg' in _format:
            location_to_save_slice = f'@Webs.ScreenCapture-{str(count)}.jpeg'
        else:
            location_to_save_slice = f'@Webs.ScreenCapture-{str(count)}.png'
        split_out = io.BytesIO()
        split_out.name = location_to_save_slice
        working_slice.save(fp=split_out, format=_format)
        location_of_image.append(split_out)
        count += 1
        await asyncio.sleep(0)
    out.close()
    return location_of_image


# https://stackoverflow.com/a/44946732/13033981
async def zipper(location_of_image: List[io.BytesIO]) -> io.BytesIO:
    zipped_file = io.BytesIO()
    with ZipFile(zipped_file, 'w') as zipper:
        for files in location_of_image:
            zipper.writestr(files.name, files.getvalue())
            files.close()
    zipped_file.name = "@Webs-Screenshot.zip"
    return zipped_file


async def metrics_graber(url: str) -> io.BytesIO:
    _pid = randint(100, 999)
    printer = Printer('statics', url, _pid)
    title, metrics = await screenshot_driver(printer)
    return await draw(title[:25], metrics)


async def draw(name: str, metrics: dict) -> io.BytesIO:
    # DBSans Font is Licensed Under Open Font License
    r = get('https://github.com/googlefonts/dm-fonts/raw/master/Sans/Exports/DMSans-Bold.ttf', allow_redirects=True)
    font = ImageFont.truetype(io.BytesIO(r.content), size=1)
    font_size = 1
    # https://stackoverflow.com/a/4902713/13033981
    while font.getsize(name)[0] < 0.90*265:
        font_size += 1
        font = ImageFont.truetype(io.BytesIO(r.content), font_size)
    font_paper = Image.new("RGB", (265, 100), color="white")
    draw = ImageDraw.Draw(font_paper)
    w, h = font.getsize(name)
    draw.text(((265-w)/2, (100-h)/2), name, font=font, fill="black")
    main_paper = Image.open(io.BytesIO(get("https://telegra.ph/file/a6a7f2e40b5ef8b1e0562.png").content))
    LOGGER.info('WEB_SCRS --> site_metrics >> main paper created')
    await asyncio.sleep(0.2)
    main_paper.paste(font_paper, (800, 460, 1065, 560))
    font_paper.close()
    metrics_paper = ''.join([f'{x} :- {y}\n' for x, y in metrics.items()])
    draw = ImageDraw.Draw(main_paper)
    font = ImageFont.truetype(io.BytesIO(r.content), 28)
    draw.multiline_text((1185, 215), metrics_paper, fill="white", font=font, spacing=15)
    LOGGER.info('WEB_SCRS --> site_metrics >> main paper rendered successfully')
    return_object = io.BytesIO()
    main_paper.save(return_object, format='png')
    main_paper.close()
    return_object.name = "@Webs-Screenshot.png"
    return return_object


async def settings_parser(link: str, inline_keyboard: list, PID: int) -> Printer:
    # starting to recognize settings
    split, resolution = False, False
    for settings in inline_keyboard:
        text = settings[0].text
        if "Format" in text:
            if "PDF" in text:
                _format = "pdf"
            else:
                _format = "png" if "PNG" in text else "jpeg"
        if "Page" in text:
            page_value = True if 'Full' in text else False
        if "Split" in text:
            split = True if 'Yes' in text else False
        if "resolution" in text:
            resolution = text
        await asyncio.sleep(0.00001)
    LOGGER.debug(f'WEB_SCRS:{PID} --> setting confirmation >> ({_format}|{page_value})')
    printer = Printer(_format, link, PID)
    if resolution:
        if '1280' in resolution:
            printer.resolution = {'width': 1280, 'height': 720}
        elif '2560' in resolution:
            printer.resolution = {'width': 2560, 'height': 1440}
        elif '640' in resolution:
            printer.resolution = {'width': 640, 'height': 480}
    if not page_value:
        printer.fullpage = False
    if split:
        printer.split = True
    return printer


async def launch_chrome(retry=False) -> Browser:
    try:
        browser = await launch(
            headless=True,
            logLevel=50,
            executablePath=EXEC_PATH,
            args=[
                '--no-sandbox',
                '--single-process',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-zygote'
            ])
        return browser
    except BadStatusLine:
        if not retry:
            LOGGER.info('WEB_SCRS --> request failed -> Excepted BadStatusLine >> retrying...')
            await asyncio.sleep(1.5)
            return await launch_chrome(True)
        elif retry:
            LOGGER.info('WEB_SCRS --> request failed -> Excepted BadStatusLine >> max retry exceeded')
            raise ResponseNotReady("Soory the site is not responding")


async def screenshot_driver(printer: Printer, tasks=[]) -> Union[List, Tuple[str, dict]]:
    if len(tasks) != 0:
        LOGGER.info(f'WEB_SCRS:{printer.PID} --> browser object >> yielded from existing task list')
        browser = tasks[0]
    else:
        LOGGER.info(f'WEB_SCRS:{printer.PID} --> no browser object exists >> creating new')
        try:
            browser = await launch_chrome()
            tasks.append(browser)
        except Exception as e:
            LOGGER.critical(e)
            raise ResponseNotReady(e)
    page = await browser.newPage()
    LOGGER.debug(f'WEB_SCRS:{printer.PID} --> created new page object >> now setting viewport')
    await page.setViewport(printer.resolution)
    LOGGER.debug(f'WEB_SCRS:{printer.PID} --> fetching received link')
    try:
        await page.goto(printer.link)
        LOGGER.debug(f'WEB_SCRS:{printer.PID} --> link fetched successfully >> now rendering page')
        if printer.type == "pdf":
            end_file = await page.pdf(printer.arguments_to_print)
        elif printer.type == "statics":
            LOGGER.debug(f'WEB_SCRS:{printer.PID} --> site metrics detected >> now rendering image')
            end_file = (await page.title(), await page.metrics())
        else:
            end_file = await page.screenshot(printer.arguments_to_print)
        return end_file
    except errors.PageError:
        LOGGER.info(f'WEB_SCRS:{printer.PID} --> request failed -> Excepted PageError >> invalid link')
        raise ResponseNotReady("Not a valid link 😓🤔")
    finally:
        await asyncio.sleep(2)
        LOGGER.debug(f'WEB_SCRS:{printer.PID} --> page rendered successfully >> now closing page object')
        await page.close()
        if len(await browser.pages()) == 1:
            LOGGER.info(f'WEB_SCRS:{printer.PID} --> no task pending >> closing browser object')
            if browser in tasks:
                tasks.remove(browser)
            await browser.close()
        elif len(await browser.pages()) < 2:
            LOGGER.info(f'WEB_SCRS:{printer.PID} --> task pending >> leaving browser intact')


async def primary_task(client: Client, msg: Message, queue=[]) -> None:
    _pid = randint(100, 999)
    link = msg.reply_to_message.text
    queue.append(link)
    LOGGER.debug(f'WEB_SCRS:{_pid} --> new request >> processing settings')
    if len(queue) > 2:
        await msg.edit("<b>You are in the queue wait for a bit ;)</b>")
        while len(queue) > 2:
            await asyncio.sleep(2)
    random_message = await msg.edit(text='<b><i>processing...</b></i>')
    printer = await settings_parser(link, msg.reply_markup.inline_keyboard, _pid)
    # logging the request into a specific group or channel
    try:
        log = int(os.environ["LOG_GROUP"])
        LOGGER.debug(f'WEB_SCRS:{printer.PID} --> LOG GROUP FOUND >> sending log')
        await client.send_message(
            log,
            f'```{msg.chat.username}```\n{printer.__str__()}')
    except Exception as e:
        LOGGER.debug(f'WEB_SCRS:{printer.PID} --> LOGGING FAILED >> {e}')
    await random_message.edit(text='<b><i>rendering.</b></i>')
    # await browser.close()
    try:
        out = io.BytesIO(await screenshot_driver(printer))
        out.name = printer.name
    except Exception as e:
        await random_message.edit(f'<b>{e}</b>')
        queue.remove(link)
        return
    await random_message.edit(text='<b><i>rendering..</b></i>')
    if printer.split and printer.fullpage:
        LOGGER.debug(f'WEB_SCRS:{printer.PID} --> split setting detected -> spliting images')
        await random_message.edit(text='<b><i>spliting images...</b></i>')
        location_of_image = await split_func(out, printer.type)
        LOGGER.debug(f'WEB_SCRS:{printer.PID} --> image splited successfully')
        # spliting finished
        if len(location_of_image) > 10:
            LOGGER.debug(f'WEB_SCRS:{printer.PID} --> found split pieces more than 10 >> zipping file')
            await random_message.edit(text='<b>detected images more than 10\n\n<i>Zipping...</i></b>')
            await asyncio.sleep(0.1)
            # zipping if length is too high
            zipped_file = await zipper(location_of_image)
            LOGGER.debug(f'WEB_SCRS:{printer.PID} --> zipping completed >> sending file')
            #  finished zipping and sending the zipped file as document
            out = zipped_file
        else:
            # sending as media group if files are not too long
            # pyrogram doesnt support InputMediaPhotot to use BytesIO
            # until its added to the library going for temporary fix
            # starting folder creartion with message id
            if not os.path.isdir('./FILES'):
                LOGGER.debug(f'WEB_SCRS:{printer.PID} --> ./FILES folder not found >> creating new ')
                os.mkdir('./FILES')
            location = f"./FILES/{str(msg.chat.id)}/{str(msg.message_id)}"
            if not os.path.isdir(location):
                LOGGER.debug(f'WEB_SCRS:{printer.PID} --> user folder not found >> creating {location}')
                os.makedirs(location)
            LOGGER.debug(f'WEB_SCRS:{printer.PID} --> sending split pieces as media group')
            for byte_objects in location_of_image:
                with open(f'{location}/{byte_objects.name}', 'wb') as writer:
                    writer.write(byte_objects.getvalue())
                byte_objects.close()
            await random_message.edit(text='<b><i>uploading...</b></i>')
            location_to_send = []
            for count, images in enumerate(location_of_image, start=1):
                location_to_send.append(InputMediaPhoto(
                    media=f'{location}/{images.name}',
                    caption=str(count)
                    ))
            # sending 10 at a time
            await client.send_chat_action(
                msg.chat.id,
                "upload_photo"
                )
            await client.send_media_group(
                media=location_to_send,
                chat_id=msg.chat.id,
                disable_notification=True
                )
            out.close()
            shutil.rmtree(location)
            LOGGER.debug(f'WEB_SCRS:{printer.PID} --> mediagroup send successfully >> request statisfied')
            queue.remove(link)
            return
    if not printer.fullpage and not printer.type == 'pdf':
        LOGGER.debug(f'WEB_SCRS:{printer.PID} --> split setting not found >> sending directly')
        await random_message.edit(text='<b><i>uploading...</b></i>')
        await client.send_chat_action(
            msg.chat.id,
            "upload_photo"
            )
        await client.send_photo(
            photo=out,
            chat_id=msg.chat.id
            )
        LOGGER.info(f'WEB_SCRS:{printer.PID} --> photo send successfully >> request statisfied')
    if (printer.type == 'pdf' or printer.fullpage):
        await client.send_chat_action(
            msg.chat.id,
            "upload_document"
        )
        await client.send_document(
            document=out,
            chat_id=msg.chat.id
        )
        LOGGER.debug(f'WEB_SCRS:{printer.PID} --> document send successfully >> request statisfied')
    out.close()
    await random_message.delete()
    queue.remove(link)
