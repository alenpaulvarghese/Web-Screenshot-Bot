# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from webshotbot import WebshotBot
from pyrogram import filters
import os


@WebshotBot.on_message(
    filters.regex(pattern="http[s]*://.+") & filters.private & ~filters.edited
)
async def checker(_, message: Message):
    msg = await message.reply_text("working", True)
    await msg.edit(
        text="Choose the prefered settings",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton(text="Format - PDF", callback_data="format")],
                [InlineKeyboardButton(text="Page - Full", callback_data="page")],
                [
                    InlineKeyboardButton(
                        text="show additional options ˅", callback_data="options"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="▫️ start render ▫️", callback_data="render"
                    )
                ],
                [InlineKeyboardButton(text="cancel", callback_data="cancel")],
            ]
        ),
    )


@WebshotBot.on_message(filters.command(["start"]))
async def start(_, message: Message) -> None:
    await message.reply_text(
        f"<b>Hi {message.from_user.first_name} 👋\n"
        "I can render website of a given link to either PDF or PNG/JPEG</b>",
        quote=True,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❓ About", callback_data="about_cb")]]
        ),
    )


@WebshotBot.on_message(filters.command(["about", "feedback"]))
async def feedback(_, message: Message) -> None:
    await message.reply_text(
        text="This project is open ❤️ source",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "👨🏻‍🦯 Source",
                        url="https://github.com/alenpaul2001/Web-Screenshot-Bot",
                    ),
                    InlineKeyboardButton(
                        "❓ Bug Report",
                        url="https://github.com/alenpaul2001/Web-Screenshot-Bot/issues",
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "🌃 Profile Icon Credit",
                        url="https://www.goodfon.com/wallpaper/art-vector-background-illustration-minimalism-angga-tanta-12.html",
                    )
                ],
            ]
        ),
    )


@WebshotBot.on_message(filters.command(["debug", "log"]) & filters.private)
async def send_log(_, message: Message) -> None:
    try:
        sudo_user = int(os.environ["SUDO_USER"])
        if sudo_user != message.chat.id:
            raise Exception
    except Exception:
        return
    if os.path.exists("debug.log"):
        await message.reply_document("debug.log")
    else:
        await message.reply_text("file not found")
