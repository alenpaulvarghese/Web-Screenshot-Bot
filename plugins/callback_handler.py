# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-
# Thanks CWPROJECTS For Helping Me
# Thanks Spechide For Supporting Me

from helper import mediagroup_gen, settings_parser, split_image
from plugins.command_handler import (  # pylint:disable=import-error
    feedback,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
)
from helper.printer import Printer
from webshotbot import WebshotBot
from pyrogram import filters
import asyncio


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "render"))
async def primary_cb(client: WebshotBot, callback_query: CallbackQuery):
    await callback_query.answer("processing your request")
    message = await callback_query.message.edit("**processing...**")
    printer = await settings_parser(
        callback_query.message.reply_to_message.text,
        callback_query.message.reply_markup.inline_keyboard,
    )
    printer.allocate_folder(
        callback_query.message.chat.id, callback_query.message.message_id
    )
    await message.edit("**rendering...**")
    try:
        await client.new_request(printer)
    except Exception as e:
        await message.edit(e)
        return
    await message.edit("**uploading...**")
    if printer.split and printer.fullpage:
        loc_of_images = await asyncio.get_event_loop().run_in_executor(
            None, split_image, printer.location, printer.file, printer.type
        )
        for media_group in mediagroup_gen(loc_of_images):
            await callback_query.message.reply_media_group(
                media_group, disable_notification=True
            )
    elif printer.type == "pdf" or printer.fullpage:
        await callback_query.message.reply_document(
            printer.file,
        )
    elif not printer.fullpage:
        await callback_query.message.reply_photo(
            printer.file,
        )
    await message.delete()


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "statics"))
async def statics_cb(client: WebshotBot, callback_query: CallbackQuery):
    await callback_query.answer("processing")
    printer = Printer("statics", callback_query.message.reply_to_message.text)
    await client.new_request(printer)
    await client.send_document(
        callback_query.message.chat.id,
        printer.file,
    )
    printer.file.close()  # type: ignore


@WebshotBot.on_callback_query()
async def keyboards_cb(_, callback_query: CallbackQuery):
    cb_data = callback_query.data
    msg = callback_query.message
    if not cb_data == "cancel":
        # cause @Spechide said so
        await callback_query.answer()
    if cb_data == "splits":
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
        await callback_query.answer("Canceled your request..!")
        await msg.delete()

    elif cb_data == "about_cb":
        await msg.delete()
        await feedback(_, msg)
