# Thanks CWPROJECTS For Helping Me
# Thanks Spechide For Supporting Me
from pyrogram import Client, Filters, InlineKeyboardButton, InputMediaPhoto
from plugins.command_handlers import blacklist, HOME, format_for_logging
from pyppeteer import launch, errors
from zipfile import ZipFile
from PIL import Image
import asyncio
import shutil
import math
import os

try:
    EXEC_PATH = os.environ.get('GOOGLE_CHROME_SHIM')
except Exception:
    print('Driver Not Found')


@Client.on_message(Filters.regex(pattern="http[s]*://.+") & Filters.private & ~Filters.edited)
async def checker(client, message):
    # https://t.me/Python/774464
    if [x for x in blacklist if x in message.text]:
        await message.reply_text("Please Dont Abuse This Service 😭😭")
    else:
        msg = await message.reply_text("working", True)
        await msg.edit(text='Choose the prefered settings', reply_markup=HOME)


@Client.on_callback_query()
async def cb_(client, callback_query):
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
        # starting folder creartion with message id
        if not os.path.isdir('./FILES'):
            os.mkdir('./FILES')
        location = f"./FILES/{str(msg.chat.id)}/{str(msg.message_id)}"
        if not os.path.isdir(location):
            os.makedirs(location)
        # logging the request into a specific group or channel
        try:
            LOGGING_GROUP = int(os.environ["LOG_GROUP"])
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
            print(f'Logging Avoided\nREASON : {e}')
        # opening chrome bin
        try:
            browser = await launch(
                headless=True,
                executablePath=EXEC_PATH
                )
            page = await browser.newPage()
            await page.goto(link, {"waitUtil": 'networkidle0'})
            await asyncio.sleep(2)
            # getting page title
            text = str(await page.title())
            if len(text) > 14:
                text = text[:14]
            text = text.replace(' ', '')
            # implementing the settings
            await random_message.edit(text='<b><i>Rendering</b></i>')
            if format == 'jpeg' or format == 'PNG':
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
                if page_value:
                    arguments_for_photo['fullPage'] = True
                await random_message.edit(text='<b><i>Rendering.</b></i>')
                # naming for the output file
                if format == 'jpeg':
                    arguments_for_photo['path'] = f'{location}/{text.strip()}-webshotbot.jpeg'
                    arguments_for_photo['type'] = 'jpeg'
                if format == 'PNG':
                    arguments_for_photo['path'] = f'{location}/{text.strip()}-webshotbot.png'
                    arguments_for_photo['type'] = 'png'
                await random_message.edit(text='<b><i>rendering...</b></i>')
                if background:
                    await asyncio.sleep(3)
                # taking screenshot and closing the browser
                await page.screenshot(arguments_for_photo)
                await browser.close()
                # spliting the image
                if split and page_value:
                    await random_message.edit(text='<b><i>Spliting Images...</b></i>')
                    # https://stackoverflow.com/questions/25705773/image-cropping-tool-python
                    Image.MAX_IMAGE_PIXELS = None
                    # https://coderwall.com/p/ovlnwa/use-python-and-pil-to-slice-an-image-vertically
                    location_of_image = []
                    img = Image.open(arguments_for_photo['path'])
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
                            location_to_save_slice = f'{location}/slice_{str(count)}.jpeg'
                        else:
                            location_to_save_slice = f'{location}/slice_{str(count)}.png'
                        location_of_image.append(location_to_save_slice)
                        working_slice.save(location_to_save_slice)
                        count += 1
                    # spliting finished
                    if len(location_of_image) > 20:
                        await random_message.edit(text='<b>detected images more than 20\n\n<i>Zipping...</i></b>')
                        await asyncio.sleep(1)
                        # zipping if length is too high
                        zipped_file = f'{location}/webshot.zip'
                        with ZipFile(zipped_file, 'w') as zipper:
                            for files in location_of_image:
                                zipper.write(files)
                        #  finished zipping and sending the zipped file as document
                        await random_message.edit(text='<b><i>uploading...</b></i>')
                        await client.send_chat_action(
                            msg.chat.id,
                            "upload_document"
                            )
                        await client.send_document(
                            document=zipped_file,
                            chat_id=msg.chat.id,
                            reply_to_message_id=msg.reply_to_message.message_id
                            )
                        # sending as media group if files are not too long
                    else:
                        await random_message.edit(text='<b><i>uploading...</b></i>')
                        location_to_send = []
                        for count, images in enumerate(location_of_image, start=1):
                            location_to_send.append(InputMediaPhoto(
                                media=images,
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
                # if split is not selected
                else:
                    await random_message.edit(text='<b><i>uploading...</b></i>')
                    if not page_value:
                        await client.send_chat_action(
                            msg.chat.id,
                            "upload_photo"
                            )
                        await client.send_photo(
                            photo=arguments_for_photo['path'],
                            chat_id=msg.chat.id,
                            reply_to_message_id=msg.reply_to_message.message_id
                            )
                    else:
                        await client.send_chat_action(
                            msg.chat.id,
                            "upload_document"
                            )
                        await client.send_document(
                            document=arguments_for_photo['path'],
                            chat_id=msg.chat.id,
                            reply_to_message_id=msg.reply_to_message.message_id
                            )
                await asyncio.sleep(1)
                await random_message.delete()
                shutil.rmtree(location)
            # configuring pdf settings
            else:
                await random_message.edit(text='<b><i>rendering.</b></i>')
                arguments_for_pdf = {}
                if resolution:
                    if '1280' in resolution:
                        arguments_for_pdf = {'width': 1280, 'height': 720}
                    elif '2560' in resolution:
                        # cause asked by <ll>//𝚂𝚊𝚢𝚊𝚗𝚝𝚑//<ll>
                        arguments_for_pdf = {'width': 2560, 'height': 1440}
                        arguments_for_pdf['scale'] = 2
                    elif '640' in resolution:
                        arguments_for_pdf = {'width': 640, 'height': 480}
                    else:
                        arguments_for_pdf = {'width': 800, 'height': 600}
                await page.emulateMedia('screen')
                arguments_for_pdf['path'] = f'{location}/{text}-webshotbot.pdf'
                if not page_value:
                    arguments_for_pdf['pageRanges'] = '1-2'
                if background:
                    await random_message.edit(text='<b><i>Rendering..</b></i>')
                    await asyncio.sleep(3)
                    arguments_for_pdf['printBackground'] = True
                await random_message.edit(text='<b><i>Rendering...</b></i>')
                await page.pdf(arguments_for_pdf)
                await random_message.edit(text='<b><i>Uploading...</b></i>')
                await client.send_chat_action(
                        msg.chat.id,
                        "upload_document"
                        )
                await browser.close()
                await client.send_document(
                        document=arguments_for_pdf['path'],
                        chat_id=msg.chat.id,
                        reply_to_message_id=msg.reply_to_message.message_id
                        )
                await asyncio.sleep(1)
                await random_message.delete()
                shutil.rmtree(location)
        except errors.PageError:
            await msg.edit(text='Not a valid link 😓🤔')
            return False
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
        if cb_data =='deleteno':
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
