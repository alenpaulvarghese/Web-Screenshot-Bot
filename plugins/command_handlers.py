from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from pyrogram import (
    Client,
    filters
)
from plugins.logger import logging  # pylint:disable=import-error
import os

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(10)

blacklist = ['drive.google.com', 'tor.checker.in']
HOME = InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Format - PDF', callback_data='format')],
            [InlineKeyboardButton(text='Page - Full', callback_data="page")],
            # [InlineKeyboardButton(text='Landscape', callback_data="orientation")],
            [InlineKeyboardButton(text='show additional options ˅', callback_data="options")],
            [InlineKeyboardButton(text='▫️ start render ▫️', callback_data="render")],
            [InlineKeyboardButton(text='cancel', callback_data="cancel")]
                            ])
format_for_logging = "Request from {name} aka @{user}\n\nQuery : {link}\n\nSettings Used : \n {settings}"


@Client.on_message(filters.command(["start"]))
async def start(client, message):
    LOGGER.debug(f"USED_CMD --> /start command >> @{message.from_user.username}")
    await client.send_message(
        chat_id=message.chat.id,
        text="Please Send Any Link",
        reply_to_message_id=message.message_id
    )


@Client.on_message(filters.command(["feedback"]))
async def feedback(client, message):
    LOGGER.debug(f"USED_CMD --> /feedback command >> @{message.from_user.username}")
    await client.send_message(
        chat_id=message.chat.id,
        text="for suggetions and feedbacks contact @STARKTM1",
        reply_to_message_id=message.message_id
    )


@Client.on_message(filters.command(["notworking"]))
async def notworking(client, message):
    LOGGER.debug(f"USED_CMD --> /notworking command >> @{message.from_user.username}")
    await client.send_message(
        chat_id=message.chat.id,
        text="Make sure Your Request has http or https prefix",
        reply_to_message_id=message.message_id
    )


@Client.on_message(filters.command(["delete"]) & filters.private)
async def deleter_(client, message):
    LOGGER.debug(f"USED_CMD --> /delete command >> @{message.from_user.username}")
    try:
        sudo_user = int(os.environ["SUDO_USER"])
    except Exception:
        LOGGER.debug('DEL__CMD --> status failed >> user not a sudo')
        return
    if message.from_user.id == sudo_user:
        random_message = await message.reply_text('Processing')
        LOGGER.debug('DEL__CMD --> status pending >> sudo user found processing')
        if os.path.isdir('./FILES/'):
            with open('walk.txt', 'w') as writer:
                for root, dirs, files in os.walk('./FILES/', topdown=False):
                    writer.write(str(root)+'\n\n'+str(dirs)+'\n\n'+str(files))
            if os.path.isfile('walk.txt'):
                LOGGER.debug('DEL__CMD --> status pending >> sending file')
                await client.send_document(
                    document='walk.txt',
                    chat_id=message.chat.id
                )
                await random_message.delete()
                os.remove('walk.txt')
                LOGGER.debug('DEL__CMD --> status pending >> waiting for user confirmation')
                await message.reply_text(
                    text='Do you want to delete?',
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text='Yes', callback_data='deleteyes')],
                        [InlineKeyboardButton(text='No', callback_data='deleteno')],
                    ])
                    )
    else:
        return


@Client.on_message(filters.command(["report"]) & filters.private)
async def delete(client, message):
    LOGGER.debug(f"USED_CMD --> /report command >> @{message.from_user.username}")
    try:
        sudo_user = int(os.environ["SUDO_USER"])
    except Exception:
        LOGGER.debug('_REPORT_ --> status failed >> no sudo user found')
        return
    if message.reply_to_message is not None:
        if message.reply_to_message.from_user.is_self:
            message_to_send = message.reply_to_message.text
            await client.send_message(
                sudo_user,
                message_to_send
            )
            LOGGER.debug('_REPORT_ --> status success >> report send')
            await message.reply_text("report successfully send")
        else:
            LOGGER.debug('_REPORT_ --> status failed >> possible spamming')
            await message.reply_text("don't spam please")
    else:
        LOGGER.debug('_REPORT_ --> status failed >> no message argument found')
        await message.reply_text("just tag the error message and use /report command")


@Client.on_message(filters.command(['debug', 'log']) & filters.private)
async def send_log(client, message):
    LOGGER.debug(f"USED_CMD --> /debug command >> @{message.from_user.username}")
    try:
        sudo_user = int(os.environ["SUDO_USER"])
        if sudo_user != message.chat.id:
            raise Exception
    except Exception:
        LOGGER.debug('DEL__CMD --> status failed >> user not a sudo')
        return
    if os.path.exists('debug.log'):
        await client.send_document(
            sudo_user,
            'debug.log'
        )
    else:
        await message.reply_text("file not found")
