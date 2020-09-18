# Thanks CWPROJECTS For Helping Me
# Thanks Spechide For Supporting Me
from plugins.command_handlers import (  # pylint:disable=import-error
    format_for_logging,
    blacklist,
    HOME
)
from pyrogram.types import (
    InlineKeyboardButton,
    InputMediaPhoto
)
from pyrogram import (
    Client,
    filters
)
from http.client import BadStatusLine
from pyppeteer import launch, errors
from plugins.logger import logging  # pylint:disable=import-error
from zipfile import ZipFile
from PIL import Image
import asyncio
import shutil
import math
import os
import io

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(10)

try:
    EXEC_PATH = os.environ.get('GOOGLE_CHROME_SHIM')
except Exception:
    LOGGER.critical('Driver Not Found')


@Client.on_message(filters.regex(pattern="http[s]*://.+") & filters.private & ~filters.edited)
async def checker(client, message):
    LOGGER.debug(f"LINK_RCV --> link received -> @{message.from_user.username} >> waiting for settings confirmation")
    # https://t.me/Python/774464
    if [x for x in blacklist if x in message.text]:
        LOGGER.debug('LINK_RCV --> link ignored >> blackisted')
        await message.reply_text("Please Dont Abuse This Service 😭😭")
    else:
        msg = await message.reply_text("working", True)
        await msg.edit(text='Choose the prefered settings', reply_markup=HOME)


@Client.on_callback_query()
async def cb_(client, callback_query, retry=False):
    cb_data = callback_query.data
    msg = callback_query.message
    if (cb_data == "render"
            or cb_data == 'cancel' or cb_data == 'statics'):
        pass
    else:
        # cause @Spechide said so
        await client.answer_callback_query(
            callback_query.id,
        )
    if cb_data == "render":
        await client.answer_callback_query(
            callback_query.id,
            text='Processing your request..!'
        )
        LOGGER.debug('WEB_SCRS --> new request >> processing settings')
        random_message = await msg.edit(text='<b><i>Processing...</b></i>')
        link = msg.reply_to_message.text
        # starting to recognize settings
        background, split, resolution = False, False, False
        for_logging = ""
        for settings in msg.reply_markup.inline_keyboard:
            if "Format" in settings[0].text:
                format = settings[0].text.split('-', 1)[1].strip()
            if "Page" in settings[0].text:
                page = settings[0].text.split('-', 1)[1].strip()
                page_value = True if 'Full' in page else False
            if "Split" in settings[0].text:
                split_boolean = settings[0].text.split('-', 1)[1].strip()
                split = True if 'Yes' in split_boolean else False
            if "wait" in settings[0].text:
                timer = settings[0].text.split('|', 1)[1].strip().strip('s')
                background = False if 'default' in timer else True
            if "resolution" in settings[0].text:
                resolution = settings[0].text.split('|', 1)[1].strip()
            for_logging += settings[0].text + '\n'
        LOGGER.debug(f'WEB_SCRS --> setting confirmation >> ({format}|{page})')
        # logging the request into a specific group or channel
        try:
            LOGGING_GROUP = int(os.environ["LOG_GROUP"])
            LOGGER.debug('WEB_SCRS --> LOG GROUP FOUND >> sending log')
            await client.send_message(
                chat_id=LOGGING_GROUP,
                text=format_for_logging.format(
                    name=msg.chat.first_name,
                    user=msg.chat.username,
                    link=link,
                    settings=for_logging
                    ),
                disable_web_page_preview=True
            )
        except Exception as e:
            LOGGER.debug(f'WEB_SCRS --> LOGGING FAILED >> {e}')
        # opening chrome bin
        try:
            LOGGER.debug('WEB_SCRS --> launching chrome')
            browser = await launch(
                headless=True,
                executablePath=EXEC_PATH
                )
            LOGGER.debug('WEB_SCRS --> fetching received link')
            page = await browser.newPage()
            await page.goto(link)
            LOGGER.debug('WEB_SCRS --> link fetched successfully')
            await asyncio.sleep(2)
            # implementing the settings
            await random_message.edit(text='<b><i>Rendering</b></i>')
            LOGGER.debug('WEB_SCRS --> configuring resolution settings')
            if format == 'jpeg' or format == 'PNG':
                LOGGER.debug('WEB_SCRS --> rendering as photo >> request statisfied')
                arguments_for_photo = {}
                # configuring resolution
                if resolution:
                    if '1280' in resolution:
                        res = {'width': 1280, 'height': 720}
                    elif '2560' in resolution:
                        res = {'width': 2560, 'height': 1440}
                    elif '640' in resolution:
                        res = {'width': 640, 'height': 480}
                    else:
                        res = {'width': 800, 'height': 600}
                    await page.setViewport(res)
                # configure btw Partial/fullpage
                LOGGER.debug('WEB_SCRS --> configuring pagesize settings')
                if page_value:
                    arguments_for_photo['fullPage'] = True
                await random_message.edit(text='<b><i>Rendering.</b></i>')
                # naming for the output file
                LOGGER.debug('WEB_SCRS --> configuring output file')
                if format == 'jpeg':
                    out_filename = '@Webs.ScreenCapture.JPEG'
                    arguments_for_photo['type'] = 'jpeg'
                if format == 'PNG':
                    out_filename = '@Webs.ScreenCapture.PNG'
                    arguments_for_photo['type'] = 'png'
                await random_message.edit(text='<b><i>Rendering...</b></i>')
                if background:
                    await asyncio.sleep(3)
                # taking screenshot and closing the browser
                LOGGER.debug('WEB_SCRS --> taking screenshot using bin')
                bytesfile = await page.screenshot(arguments_for_photo)
                LOGGER.debug('WEB_SCRS --> closing chrome binary')
                await browser.close()
                LOGGER.debug('WEB_SCRS --> chrome bin closed successfully')
                # spliting the image
                with io.BytesIO(bytesfile) as out:
                    out.name = out_filename
                    if split and page_value:
                        LOGGER.debug('WEB_SCRS --> split setting detected -> spliting images')
                        await random_message.edit(text='<b><i>Spliting Images...</b></i>')
                        # https://stackoverflow.com/questions/25705773/image-cropping-tool-python
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
                            if 'jpeg' in format:
                                location_to_save_slice = f'@Webs.ScreenCapture-{str(count)}.jpeg'
                            else:
                                location_to_save_slice = f'@Webs.ScreenCapture-{str(count)}.png'
                            split_out = io.BytesIO()
                            split_out.name = location_to_save_slice
                            working_slice.save(fp=split_out, format=arguments_for_photo['type'])
                            location_of_image.append(split_out)
                            count += 1
                        LOGGER.debug(f'WEB_SCRS --> image splited successfully >> total piece({count})')
                        out.close()
                        # spliting finished
                        if len(location_of_image) > 20:
                            LOGGER.debug('WEB_SCRS --> found split pieces more than 20 >> zipping file')
                            await random_message.edit(text='<b>detected images more than 20\n\n<i>Zipping...</i></b>')
                            await asyncio.sleep(1)
                            # zipping if length is too high
                            # https://stackoverflow.com/a/44946732/13033981
                            zipped_file = io.BytesIO()
                            with ZipFile(zipped_file, 'w') as zipper:
                                for files in location_of_image:
                                    zipper.writestr(files.name, files.getvalue())
                                    files.close()
                            zipped_file.name = "@Webs-Screenshot.zip"
                            LOGGER.debug('WEB_SCRS --> zipping completed >> sending file')
                            #  finished zipping and sending the zipped file as document
                            await random_message.edit(text='<b><i>Uploading...</b></i>')
                            await client.send_chat_action(
                                msg.chat.id,
                                "upload_document"
                                )
                            await client.send_document(
                                document=zipped_file,
                                chat_id=msg.chat.id,
                                reply_to_message_id=msg.reply_to_message.message_id
                                )
                            LOGGER.debug('WEB_SCRS --> file send successfully >> request statisfied')
                            zipped_file.close()
                        # sending as media group if files are not too long
                        # pyrogram doesnt support InputMediaPhotot to use BytesIO
                        # until its added to the library going for temporary fix
                        else:
                            # starting folder creartion with message id
                            if not os.path.isdir('./FILES'):
                                LOGGER.debug('WEB_SCRS --> ./FILES folder not found >> creating new ')
                                os.mkdir('./FILES')
                            location = f"./FILES/{str(msg.chat.id)}/{str(msg.message_id)}"
                            if not os.path.isdir(location):
                                LOGGER.debug(f'WEB_SCRS --> user folder not found >> creating {location}')
                                os.makedirs(location)
                            LOGGER.debug('WEB_SCRS --> sending split pieces as media group')
                            for byte_objects in location_of_image:
                                with open(f'{location}/{byte_objects.name}', 'wb') as writer:
                                    writer.write(byte_objects.getvalue())
                                byte_objects.close()
                            await random_message.edit(text='<b><i>Uploading...</b></i>')
                            location_to_send = []
                            for count, images in enumerate(location_of_image, start=1):
                                location_to_send.append(InputMediaPhoto(
                                    media=f'{location}/{images.name}',
                                    caption=str(count)
                                    ))
                            sent_so_far = 0
                            # sending 10 at a time
                            while sent_so_far <= len(location_to_send):
                                await client.send_chat_action(
                                    msg.chat.id,
                                    "upload_photo"
                                    )
                                await client.send_media_group(
                                    media=location_to_send[sent_so_far:sent_so_far+10],
                                    chat_id=msg.chat.id,
                                    reply_to_message_id=msg.reply_to_message.message_id,
                                    disable_notification=True
                                    )
                                sent_so_far += 10
                                await asyncio.sleep(0.5)
                            shutil.rmtree(location)
                            LOGGER.debug('WEB_SCRS --> mediagroup send successfully >> request statisfied')
                        # closing every Bytesio to save memory
                        [x.close() for x in location_of_image]
                    # if split is not selected
                    else:
                        LOGGER.debug('WEB_SCRS --> split setting not found >> sending directly')
                        await random_message.edit(text='<b><i>Uploading...</b></i>')
                        if not page_value:
                            await client.send_chat_action(
                                msg.chat.id,
                                "upload_photo"
                                )
                            await client.send_photo(
                                photo=out,
                                chat_id=msg.chat.id,
                                reply_to_message_id=msg.reply_to_message.message_id
                                )
                            LOGGER.debug('WEB_SCRS --> photo send successfully >> request statisfied')
                        else:
                            await client.send_chat_action(
                                msg.chat.id,
                                "upload_document"
                                )
                            await client.send_document(
                                document=out,
                                chat_id=msg.chat.id,
                                reply_to_message_id=msg.reply_to_message.message_id
                                )
                            LOGGER.debug('WEB_SCRS --> document send successfully >> request statisfied')
                await asyncio.sleep(1)
                await random_message.delete()
                out.close()
            # configuring pdf settings
            else:
                LOGGER.debug('WEB_SCRS --> rendering as PDF >> processing settings')
                await random_message.edit(text='<b><i>Rendering.</b></i>')
                arguments_for_pdf = {}
                if resolution:
                    if '1280' in resolution:
                        arguments_for_pdf = {'width': 1280, 'height': 720}
                    elif '2560' in resolution:
                        # cause asked by <ll>//𝚂𝚊𝚢𝚊𝚗𝚝𝚑//<ll>
                        arguments_for_pdf = {'width': 2560, 'height': 1440}
                    elif '640' in resolution:
                        arguments_for_pdf = {'width': 640, 'height': 480}
                    else:
                        arguments_for_pdf = {'width': 800, 'height': 600}
                arguments_for_pdf['format'] = 'Letter'
                arguments_for_pdf['displayHeaderFooter'] = True
                arguments_for_pdf['margin'] = {"bottom": 70, "left": 25, "right": 35, "top": 40}
                await page.emulateMedia('screen')
                if not page_value:
                    arguments_for_pdf['pageRanges'] = '1-2'
                LOGGER.debug('WEB_SCRS --> configuration successfull >> waiting to render')
                if background:
                    await random_message.edit(text='<b><i>Rendering..</b></i>')
                    await asyncio.sleep(3)
                    arguments_for_pdf['printBackground'] = True
                await random_message.edit(text='<b><i>Rendering...</b></i>')
                LOGGER.debug('WEB_SCRS --> rendering pdf')
                bytes_pdf = await page.pdf(arguments_for_pdf)
                await browser.close()
                LOGGER.debug('WEB_SCRS --> PDF rendered >> closing bin')
                await random_message.edit(text='<b><i>Uploading...</b></i>')
                await client.send_chat_action(
                        msg.chat.id,
                        "upload_document"
                        )
                with io.BytesIO(bytes_pdf) as out:
                    out.name = "@Webs.ScreenCapture.pdf"
                    await client.send_document(
                            document=out,
                            chat_id=msg.chat.id,
                            reply_to_message_id=msg.reply_to_message.message_id
                            )
                LOGGER.debug('WEB_SCRS --> PDF document send successfully >> request statisfied')
                await random_message.delete()
                await asyncio.sleep(1)
        except errors.PageError:
            LOGGER.debug('WEB_SCRS --> request failed -> Excepted PageError >> invalid link')
            await msg.edit(text='Not a valid link 😓🤔')
            await browser.close()
            return
        except BadStatusLine:
            await browser.close()
            if not retry:
                LOGGER.debug('WEB_SCRS --> request failed -> Excepted BadStatusLine >> retrying...')
                await msg.edit("<b>Site Error\nRetrying....</b>")
                await asyncio.sleep(4)
                await cb_(client, callback_query, retry=True)
            elif retry:
                LOGGER.debug('WEB_SCRS --> request failed -> Excepted BadStatusLine >> max retry exceeded')
                await msg.edit("<b>Soory the site is not responding</b>")
                return False
        except ModuleNotFoundError as e:
            await browser.close()
            LOGGER.debug(f'WEB_SCRS --> request failed -> Excepted {e}')
            await msg.reply_to_message.reply_text(
                f'''something went wrong\n
<b>reason:</b>\n\n<code>{e}</code>\n
<i>do a anonymous reporting to the developer
by tagging this message and use <code>/report</code> command</i>\n\n
retry if possible...''',
                quote=True
                )

    elif cb_data == "splits":
        if "PDF" not in msg.reply_markup.inline_keyboard[0][0].text:
            index_number = 1
        current_boolean = msg.reply_markup.inline_keyboard[index_number][0]
        boolean_to_change = 'Split - No' if "Yes" in current_boolean.text else 'Split - Yes'
        msg.reply_markup.inline_keyboard[index_number][0]['text'] = boolean_to_change
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == "page":
        if 'PDF' in msg.reply_markup.inline_keyboard[0][0].text:
            index_number = 1
        else:
            index_number = 2
        current_page = msg.reply_markup.inline_keyboard[index_number][0]
        page_to_change = "Page - Partial" if "Full" in current_page.text else "Page - Full"
        msg.reply_markup.inline_keyboard[index_number][0]['text'] = page_to_change
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == 'timer':
        current_time = msg.reply_markup.inline_keyboard[-4][0].text
        time_to_change = "wait for | BackgroundToLoad" if 'default' in current_time else "wait for | default"
        msg.reply_markup.inline_keyboard[-4][0]['text'] = time_to_change
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == 'options':
        current_option = msg.reply_markup.inline_keyboard[-3][0].text
        options_to_change = "hide additional options ˄" if 'show' in current_option else 'show additional options ˅'
        if 'hide' in options_to_change:
            msg.reply_markup.inline_keyboard.insert(
                -2,
                [InlineKeyboardButton(text="resolution | 800x600", callback_data='res')]
            )
            msg.reply_markup.inline_keyboard.insert(
                -2,
                [InlineKeyboardButton(text='wait for | default', callback_data="timer")],
            )
            msg.reply_markup.inline_keyboard.insert(
                -2,
                [InlineKeyboardButton(text='▫️ site statitics ▫️', callback_data="statics")],
            )
            if 'PDF' in msg.reply_markup.inline_keyboard[0][0].text:
                index_to_change = 2
            else:
                index_to_change = 3
            msg.reply_markup.inline_keyboard[index_to_change][0]['text'] = options_to_change

        else:
            for _ in range(3):
                msg.reply_markup.inline_keyboard.pop(-3)
            msg.reply_markup.inline_keyboard[-3][0]['text'] = options_to_change
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == "res":
        current_res = msg.reply_markup.inline_keyboard[-5][0].text
        if '800' in current_res:
            res_to_change = "resolution | 1280x720"
        elif '1280' in current_res:
            # cause asked by <ll>//𝚂𝚊𝚢𝚊𝚗𝚝𝚑//<ll>
            res_to_change = "resolution | 2560x1440"
        elif '2560' in current_res:
            res_to_change = "resolution | 640x480"
        else:
            res_to_change = "resolution | 800x600"
        msg.reply_markup.inline_keyboard[-5][0]['text'] = res_to_change
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == "format":
        current_format = msg.reply_markup.inline_keyboard[0][0]
        if 'PDF' in current_format.text:
            format_to_change = 'Format - PNG'
        elif 'PNG' in current_format.text:
            format_to_change = 'Format - jpeg'
        elif 'jpeg' in current_format.text:
            format_to_change = 'Format - PDF'
        msg.reply_markup.inline_keyboard[0][0]['text'] = format_to_change
        if "PNG" in format_to_change:
            msg.reply_markup.inline_keyboard.insert(
                1,
                [InlineKeyboardButton(text="Split - No", callback_data='splits')]
            )
        if 'PDF' in format_to_change:
            if "Split" in msg.reply_markup.inline_keyboard[1][0].text:
                msg.reply_markup.inline_keyboard.pop(1)
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == "cancel":
        await client.answer_callback_query(
            callback_query.id,
            text='Canceled your request..!'
        )
        await msg.delete()
    elif cb_data == 'statics':
        await client.answer_callback_query(
            callback_query.id,
            text='Soory this features is not implemented yet😫😢😬!',
            show_alert=True
        )
    elif cb_data == 'deleteno' or cb_data == 'deleteyes':
        if cb_data == 'deleteno':
            await msg.edit(text='process canceled')
            await asyncio.sleep(2)
            await msg.delete()
        else:
            await msg.edit(text='deleteing')
            try:
                shutil.rmtree('./FILES/')
            except Exception as e:
                await msg.edit(text=e)
            finally:
                await asyncio.sleep(2)
                await msg.delete()
