# Thanks CWPROJECTS For Helping Me
# Thanks Spechide For Supporting Me
from pyrogram import Client, Filters, InlineKeyboardButton
from plugins.slicer_tool import long_slice, text_message, blacklist, HOME
from pyppeteer import launch, errors
from PIL import Image
import asyncio
import time
import os

try:
    EXEC_PATH = os.environ.get('GOOGLE_CHROME_SHIM')
except Exception as e:
    print('Driver Not Found')


async def mainer(link):#, path, is_image):
    browser = await launch(
        headless=True,
        executablePath=EXEC_PATH
        )
    page = await browser.newPage()
    await page.goto(link)
    text = await page.title()
    # if is_image:
    #     await page.screenshot({'path': f'{path}', 'fullPage': True, 'type': 'png'})
    # else:
    #     await page.pdf({'path': f'{path}'})
    await browser.close()
    return text

@Client.on_message(Filters.regex(pattern="http[s]*://.+") & Filters.private)
async def checker(client, message):
    # https://t.me/Python/774464
    if [x for x in blacklist if x in message.text]:
        await message.reply_text("Please Dont Abuse This Service 😭😭")
    else:
        msg = await message.reply_text("working", True)
        # Logger
        try:
            LOGGING_GROUP = "-1001486335201"
            # LOGGING_GROUP = os.environ.get('LOG_GROUP')
            await client.send_message(
                chat_id=LOGGING_GROUP,
                text=f"Request from {message.chat.first_name} aka @{message.chat.username}\n\nQuery : {message.text}",
                disable_web_page_preview=True
            )
        except Exception as e:
            print(f'Logging Avoided\nREASON : {e}')

        await msg.edit(text='Choose the prefered settings', reply_markup=HOME)


@Client.on_callback_query()
async def cb_(client, callback_query):
    cb_data = callback_query.data
    msg = callback_query.message

    if not os.path.isdir('./FILES/'):
        os.mkdir('./FILES/')
    tmp_dir = './FILES/' + str(callback_query.message.chat.id) + "/"
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)

    # https://medium.com/@epicshane/one-liner-for-python-if-elif-else-statements-d9d46016ba2a
    file = {cb_data == 'to_img': tmp_dir+"image.png", cb_data == 'to_pdf': tmp_dir+'image.pdf'}.get(True, tmp_dir+"image.png")

    if cb_data == "to_img" or cb_data == "to_pdf":
        url = callback_query.message.reply_to_message.text 
        mode = True if cb_data == "to_img" else False
        await msg.edit('Trying to Render...')
        # Main Function
        try:
            await mainer(url, file, mode)
        except errors.PageError as e:
            await msg.edit(text='Not a valid link 😓🤔')
            return False
        await msg.edit('Succefully Rendered')
        if cb_data == "to_img":
            dimension = Image.open(file)
            width, height = dimension.size
            await asyncio.sleep(3)
            await msg.edit(text=f'**Image Description**\nwidth  : {width}\nheight : {height}')
            await asyncio.sleep(2.5)
            if height > 4000:
                await msg.reply_text(text=text_message,
                                     reply_markup=InlineKeyboardMarkup([
                                            [InlineKeyboardButton(text='yes', callback_data='split')],
                                            [InlineKeyboardButton(text='no', callback_data='dont_split')]
                                    ])
                  )
                return

        await msg.edit('Uploading...')
        await client.send_document(
            document=file,
            chat_id=callback_query.message.chat.id
        )
        await msg.delete()
        os.remove(file)

    elif cb_data == "split" or cb_data == "dont_split":
        if cb_data == "dont_split":
            await msg.edit('Uploading...')
            await client.send_document(
                document=file,
                chat_id=callback_query.message.chat.id
            )
            os.remove(file)
        else:
            id_of_the_chat = callback_query.message.chat.id
            await msg.edit("uploading")
            await long_slice(
                file,
                str(id_of_the_chat),
                id_of_the_chat,
                client
                )
        await msg.delete()
    elif cb_data == "render":
        link = msg.reply_to_message.text
        quality, split = None, None
        for settings in msg.reply_markup.inline_keyboard:
            if "Format" in settings[0].text:
                format = settings[0].text.split('-', 1)[1].strip()
            if "Page" in settings[0].text:
                page = settings[0].text.split('-', 1)[1].strip()
                page_value = True if 'Full' in page else False
            if format == 'jpeg' and 'Quality' in settings[0].text:
                quality = settings[0].text.split('-', 1)[1].strip().strip('%')
            if "Split" in settings[0].text:
                split_boolean = settings[0].text.split('-', 1)[1].strip()
                split = True if 'Yes' in split_boolean else False
            if "wait" in settings[0].text:
                timer = settings[0].text.split('|', 1)[1].strip().strip('s')
        print(format, page_value, split, timer, quality)
        # starting folder creartion with message id
        if not os.path.isdir('./FILES'):
            os.mkdir('./FILES')
        location = f"./FILES/{str(msg.chat.id)}/{str(msg.message_id)}"
        if not os.path.isdir(location):
            os.makedirs(location)
        browser = await launch(
            headless=True,
            executablePath=EXEC_PATH
            )
        page = await browser.newPage()
        await page.goto(link)
        text = str(await page.title())
        background = False
        if timer != 'default':
            background = True
        if format == 'jpeg' or format == 'PNG':
            arguments_for_photo = {}
            if page_value:
                arguments_for_photo['fullPage'] = True
            if format == 'jpeg':
                arguments_for_photo['path'] = f'{location}/{text.strip()}-webshotbot.JPEG' 
                arguments_for_photo['type'] = 'jpeg'
                if '50' in quality:
                    print('rendering with 50%')
                    arguments_for_photo['quality'] = 1
                elif '100' in quality:
                    print('rendering with 100%')
                    arguments_for_photo['quality'] = 100
            print(arguments_for_photo)
            await page.screenshot(arguments_for_photo)
        if False:
            await page.screenshot({'path': f'{path}', 'fullPage': True, 'type': 'png'})
        else:
            arguments_for_pdf = {'format': 'A4'}
            arguments_for_pdf 
            arguments_for_pdf['path'] = f'{location}/{text.strip()}-webshotbot.pdf'
            if not page_value:
                arguments_for_pdf['pageRanges'] = '1-2'
            if background:
                arguments_for_pdf['printBackground'] = True
            print(arguments_for_pdf)
            await page.pdf(arguments_for_pdf)
        await browser.close()



    elif cb_data == "quality":
        current_quality = msg.reply_markup.inline_keyboard[1][0]
        quality_to_change = "Quality - 100%" if "50" in current_quality.text else "Quality - 50%"
        msg.reply_markup.inline_keyboard[1][0]['text'] = quality_to_change
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == "splits":
        if "PNG" in msg.reply_markup.inline_keyboard[0][0].text:
            index_number = 1
        else:
            index_number = 2
        current_boolean = msg.reply_markup.inline_keyboard[index_number][0]
        boolean_to_change = 'Split - No' if "Yes" in current_boolean.text else 'Split - Yes'
        msg.reply_markup.inline_keyboard[index_number][0]['text'] = boolean_to_change
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == "page":
        current_page = msg.reply_markup.inline_keyboard[-4][0]
        page_to_change = "Page - Partial" if "Full" in current_page.text else "Page - Full"
        msg.reply_markup.inline_keyboard[-4][0]['text'] = page_to_change
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == 'timer':
        current_time = msg.reply_markup.inline_keyboard[-3][0].text
        time_to_change = "wait for | BackgroundToLoad" if 'default' in current_time else "wait for | default"
        msg.reply_markup.inline_keyboard[-3][0]['text'] = time_to_change
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
        if format_to_change == 'Format - jpeg':
            msg.reply_markup.inline_keyboard.insert(
                1,
                [InlineKeyboardButton(text="Quality - 50%", callback_data='quality')]
            )
        if "PNG" in format_to_change:
            msg.reply_markup.inline_keyboard.insert(
                1,
                [InlineKeyboardButton(text="Split - Yes", callback_data='splits')]
            )
        if 'PDF' in format_to_change:
            if "Quality" in msg.reply_markup.inline_keyboard[1][0].text:
                msg.reply_markup.inline_keyboard.pop(1)
            if "Split" in msg.reply_markup.inline_keyboard[1][0].text:
                msg.reply_markup.inline_keyboard.pop(1)
        await msg.edit(text='Choose the prefered settings', reply_markup=msg.reply_markup)

    elif cb_data == "cancel":
        await msg.delete()
