# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import asyncio

from pyrogram import filters
from pyrogram.enums import ChatAction
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from helper import mediagroup_gen
from helper.callback import extract_render_type, get_resolution
from helper.images import split_image
from helper.printer import Printer, RenderType, ScrollMode
from plugins.command_handler import feedback
from webshotbot import WebshotBot


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "render"))  # type: ignore
async def primary_cb(client: WebshotBot, callback_query: CallbackQuery):
    await callback_query.answer("processing your request")
    message = await callback_query.message.edit("**processing...**")
    printer = Printer.from_message(callback_query.message)
    printer.allocate_folder(callback_query.message.chat.id, callback_query.message.id)
    await message.edit("**please wait you are in a queue...**")
    try:
        future, wait_event = client.new_request(printer, callback_query.message.chat.id)
        await wait_event.wait()
        await message.edit(
            "**rendering the website...**",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("render now", "release")]])
            if printer.scroll_control == ScrollMode.MANUAL
            else None,  # type: ignore
        )
        if Config.LOG_GROUP is not None:
            await client.send_message(
                Config.LOG_GROUP,
                printer._get_logstr(
                    callback_query.message.reply_to_message.from_user.id,
                    callback_query.message.reply_to_message.from_user.first_name,
                ),
            )
        await future
    except Exception as e:
        await message.edit(f"`{e}`")
        printer.cleanup()
        return
    await message.edit("**uploading...**")
    if printer.split and printer.fullpage:
        loc_of_images = await asyncio.get_event_loop().run_in_executor(None, split_image, printer.file)
        for media_group in mediagroup_gen(loc_of_images):
            await asyncio.gather(
                callback_query.message.reply_chat_action(ChatAction.UPLOAD_PHOTO),
                callback_query.message.reply_media_group(media_group, disable_notification=True),  # type: ignore
            )
    elif printer.type == RenderType.PDF or printer.fullpage:
        await asyncio.gather(
            callback_query.message.reply_chat_action(ChatAction.UPLOAD_DOCUMENT),
            callback_query.message.reply_document(printer.file),
        )
    elif not printer.fullpage:
        await asyncio.gather(
            callback_query.message.reply_chat_action(ChatAction.UPLOAD_PHOTO),
            callback_query.message.reply_photo(printer.file),
        )
    await asyncio.gather(
        message.delete(),
        message.reply_text('__Please toggle "Scroll Site" setting if the output has no content.__'),
    )
    printer.cleanup()


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "release"))  # type: ignore
async def release_cb(client: WebshotBot, callback_query: CallbackQuery):
    event = client.get_request(callback_query.message.chat.id)
    if event is not None:
        event.set()
        await callback_query.answer("rendering now")
        await callback_query.message.edit_reply_markup()
    else:
        await callback_query.answer("please wait")


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "res"))  # type: ignore
@extract_render_type
async def resolution_cb(_, callback_query: CallbackQuery, render_type: RenderType):
    await callback_query.answer()
    message = callback_query.message
    current_res = message.reply_markup.inline_keyboard[4][0].text  # type: ignore
    button_title = "resolution | "
    current_res = current_res.removeprefix(button_title)
    res_to_change = button_title + get_resolution(current_res=current_res, render_type=render_type)
    message.reply_markup.inline_keyboard[4][0] = InlineKeyboardButton(res_to_change, "res")  # type: ignore
    await message.edit(text="Choose the prefered settings", reply_markup=message.reply_markup)  # type: ignore


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "format"))  # type: ignore
@extract_render_type
async def format_cb(_, callback_query: CallbackQuery, render_type: RenderType):
    await callback_query.answer()
    message = callback_query.message
    reply_markup: InlineKeyboardMarkup = message.reply_markup  # type: ignore
    if render_type == RenderType.PDF:
        format_to_change = "Format - PNG"
        if "hide" in reply_markup.inline_keyboard[3][0].text:
            # Change to resolution from pdf format.
            reply_markup.inline_keyboard[4][0] = InlineKeyboardButton("resolution | 1280x720", "res")
            # Add the split button.
            reply_markup.inline_keyboard.insert(-2, [InlineKeyboardButton(text="Split - No", callback_data="splits")])
    elif render_type == RenderType.JPEG:
        format_to_change = "Format - PDF"
        if "hide" in reply_markup.inline_keyboard[3][0].text:
            # Change to pdf format from resolution.
            reply_markup.inline_keyboard[4][0] = InlineKeyboardButton("resolution | Letter", "res")
            # Remove the split button because it is not applicable for PDF.
            reply_markup.inline_keyboard.pop(-3)
    else:
        format_to_change = "Format - JPEG"
    reply_markup.inline_keyboard[0][0] = InlineKeyboardButton(format_to_change, "format")
    await message.edit(text="Choose the prefered settings", reply_markup=reply_markup)


@WebshotBot.on_callback_query(filters.create(lambda _, __, c: c.data == "options"))  # type: ignore
@extract_render_type
async def options_cb(_, callback_query: CallbackQuery, render_type: RenderType):
    reply_markup: InlineKeyboardMarkup = callback_query.message.reply_markup  # type: ignore
    toggled = "show" in reply_markup.inline_keyboard[3][0].text
    await callback_query.answer(f"{'opening' if toggled else'closing'} additional settings")
    if toggled:
        resolution = "Letter" if render_type == RenderType.PDF else "1280x720"
        reply_markup.inline_keyboard.insert(
            -2,
            [InlineKeyboardButton(text=f"resolution | {resolution}", callback_data="res")],
        )
        if render_type != RenderType.PDF:
            reply_markup.inline_keyboard.insert(
                -2,
                [InlineKeyboardButton(text="Split - No", callback_data="splits")],
            )
    else:
        for _ in range((1 if render_type == RenderType.PDF else 2)):
            reply_markup.inline_keyboard.pop(-3)
    options_to_change = "hide additional options ˄" if toggled else "show additional options ˅"
    reply_markup.inline_keyboard[3][0] = InlineKeyboardButton(options_to_change, "options")
    await callback_query.message.edit(text="Choose the prefered settings", reply_markup=reply_markup)


@WebshotBot.on_callback_query()  # type: ignore
async def configurations_cb(_, callback_query: CallbackQuery):
    cb_data = callback_query.data
    message = callback_query.message
    reply_markup: InlineKeyboardMarkup = message.reply_markup  # type: ignore
    if not cb_data == "cancel":
        # cause @Spechide said so
        await callback_query.answer()
    if cb_data == "splits":
        current_boolean = reply_markup.inline_keyboard[-3][0]
        reply_markup.inline_keyboard[-3][0] = InlineKeyboardButton(
            ("Split - No" if "Yes" in current_boolean.text else "Split - Yes"),
            "splits",
        )
        await message.edit(text="Choose the prefered settings", reply_markup=reply_markup)

    elif cb_data == "page":
        current_page = reply_markup.inline_keyboard[1][0]
        reply_markup.inline_keyboard[1][0] = InlineKeyboardButton(
            ("Page - Partial" if "Full" in current_page.text else "Page - Full"), "page"
        )
        await message.edit(text="Choose the prefered settings", reply_markup=reply_markup)

    elif cb_data == "scroll":
        current_load = reply_markup.inline_keyboard[2][0]
        if "No" in current_load.text:
            text = "Auto"
        elif "Auto" in current_load.text:
            text = "Manual"
        elif "Manual" in current_load.text:
            text = "No"
        reply_markup.inline_keyboard[2][0] = InlineKeyboardButton(f"Scroll Site - {text}", "scroll")
        await message.edit(text="Choose the prefered settings", reply_markup=reply_markup)

    elif cb_data == "cancel":
        await callback_query.answer("Canceled your request..!")
        await message.delete()

    elif cb_data == "about_cb":
        await message.delete()
        await feedback(_, message)
