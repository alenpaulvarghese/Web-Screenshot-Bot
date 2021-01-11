# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-
# Thanks CWPROJECTS For Helping Me
# Thanks Spechide For Supporting Me

from plugins.command_handlers import (  # pylint:disable=import-error
    BLACKLIST,
    feedback,
    HOME,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
)
from pyrogram import Client, filters
from plugins.tool_bundle import (  # pylint:disable=import-error
    metrics_graber,
    primary_task,
)
from plugins.logger import logging  # pylint:disable=import-error
import asyncio
import shutil

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(10)


@Client.on_message(
    filters.regex(pattern="http[s]*://.+") & filters.private & ~filters.edited
)
async def checker(client: Client, message):
    LOGGER.debug(
        f"LINK_RCV --> link received -> @{message.from_user.username} >> waiting for settings confirmation"
    )
    # https://t.me/Python/774464
    if [x for x in BLACKLIST if x in message.text]:
        LOGGER.debug("LINK_RCV --> link ignored >> blackisted")
        await message.reply_text("Please Dont Abuse This Service 😭😭")
    else:
        msg = await message.reply_text("working", True)
        await msg.edit(text="Choose the prefered settings", reply_markup=HOME)


@Client.on_callback_query()
async def cb_(client: Client, callback_query: CallbackQuery, retry=False):
    cb_data = callback_query.data
    msg = callback_query.message
    if cb_data == "render" or cb_data == "cancel" or cb_data == "statics":
        pass
    else:
        # cause @Spechide said so
        await client.answer_callback_query(
            callback_query.id,
        )
    if cb_data == "render":
        await client.answer_callback_query(
            callback_query.id, text="Processing your request..!"
        )
        await primary_task(client, msg)
    elif cb_data == "splits":
        if "PDF" not in msg.reply_markup.inline_keyboard[0][0].text:
            index_number = 1
        current_boolean = msg.reply_markup.inline_keyboard[index_number][0]
        boolean_to_change = (
            "Split - No" if "Yes" in current_boolean.text else "Split - Yes"
        )
        msg.reply_markup.inline_keyboard[index_number][0]["text"] = boolean_to_change
        await msg.edit(
            text="Choose the prefered settings", reply_markup=msg.reply_markup
        )

    elif cb_data == "page":
        if "PDF" in msg.reply_markup.inline_keyboard[0][0].text:
            index_number = 1
        else:
            index_number = 2
        current_page = msg.reply_markup.inline_keyboard[index_number][0]
        page_to_change = (
            "Page - Partial" if "Full" in current_page.text else "Page - Full"
        )
        msg.reply_markup.inline_keyboard[index_number][0]["text"] = page_to_change
        await msg.edit(
            text="Choose the prefered settings", reply_markup=msg.reply_markup
        )

    elif cb_data == "options":
        current_option = msg.reply_markup.inline_keyboard[-3][0].text
        options_to_change = (
            "hide additional options ˄"
            if "show" in current_option
            else "show additional options ˅"
        )
        if "hide" in options_to_change:
            msg.reply_markup.inline_keyboard.insert(
                -2,
                [
                    InlineKeyboardButton(
                        text="resolution | 800x600", callback_data="res"
                    )
                ],
            )
            msg.reply_markup.inline_keyboard.insert(
                -2,
                [
                    InlineKeyboardButton(
                        text="▫️ site statitics ▫️", callback_data="statics"
                    )
                ],
            )
            if "PDF" in msg.reply_markup.inline_keyboard[0][0].text:
                index_to_change = 2
            else:
                index_to_change = 3
            msg.reply_markup.inline_keyboard[index_to_change][0][
                "text"
            ] = options_to_change
        else:
            for _ in range(2):
                msg.reply_markup.inline_keyboard.pop(-3)
            msg.reply_markup.inline_keyboard[-3][0]["text"] = options_to_change
        await msg.edit(
            text="Choose the prefered settings", reply_markup=msg.reply_markup
        )

    elif cb_data == "res":
        current_res = msg.reply_markup.inline_keyboard[-4][0].text
        if "800" in current_res:
            res_to_change = "resolution | 1280x720"
        elif "1280" in current_res:
            # cause asked by <ll>//𝚂𝚊𝚢𝚊𝚗𝚝𝚑//<ll>
            res_to_change = "resolution | 2560x1440"
        elif "2560" in current_res:
            res_to_change = "resolution | 640x480"
        else:
            res_to_change = "resolution | 800x600"
        msg.reply_markup.inline_keyboard[-4][0]["text"] = res_to_change
        await msg.edit(
            text="Choose the prefered settings", reply_markup=msg.reply_markup
        )

    elif cb_data == "format":
        current_format = msg.reply_markup.inline_keyboard[0][0]
        if "PDF" in current_format.text:
            format_to_change = "Format - PNG"
        elif "PNG" in current_format.text:
            format_to_change = "Format - JPEG"
        elif "JPEG" in current_format.text:
            format_to_change = "Format - PDF"
        msg.reply_markup.inline_keyboard[0][0]["text"] = format_to_change
        if "PNG" in format_to_change:
            msg.reply_markup.inline_keyboard.insert(
                1, [InlineKeyboardButton(text="Split - No", callback_data="splits")]
            )
        if "PDF" in format_to_change:
            if "Split" in msg.reply_markup.inline_keyboard[1][0].text:
                msg.reply_markup.inline_keyboard.pop(1)
        await msg.edit(
            text="Choose the prefered settings", reply_markup=msg.reply_markup
        )

    elif cb_data == "cancel":
        await client.answer_callback_query(
            callback_query.id, text="Canceled your request..!"
        )
        await msg.delete()
    elif cb_data == "statics":
        await callback_query.answer(
            "Processing the website...",
        )
        await msg.delete()
        t = await msg.reply_text("<b>processing...</b>")
        try:
            main_paper = await metrics_graber(msg.reply_to_message.text)
            await msg.reply_photo(main_paper)
            LOGGER.info("WEB_SCRS --> site_metrics >> request satisfied")
        except Exception as e:
            await msg.reply_text(f"<b>{e}</b>")
            LOGGER.info(f"WEB_SCRS --> site_metrics -> request faild >> {e}")
        finally:
            await t.delete()
    elif cb_data == "deleteno" or cb_data == "deleteyes":
        if cb_data == "deleteno":
            await msg.edit(text="process canceled")
            await asyncio.sleep(2)
            await msg.delete()
        else:
            await msg.edit(text="deleteing")
            try:
                shutil.rmtree("./FILES/")
            except Exception as e:
                await msg.edit(text=e)
            finally:
                await asyncio.sleep(2)
                await msg.delete()
    elif cb_data == "about_cb":
        await msg.delete()
        await feedback(client, msg)
