# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import os

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import Config
from helper.printer import CacheData, RenderType, ScrollMode
from webshotbot import WebshotBot


@WebshotBot.on_message(
    filters.regex(pattern="http[s]*://.+") & filters.private & ~filters.create(lambda _, __, m: bool(m.edit_date))
)
async def checker(client: WebshotBot, message: Message):
    msg = await message.reply_text("working", True)
    markup = []
    _settings = client.get_settings_cache(message.chat.id)
    if _settings is None:
        _settings = CacheData(
            render_type=RenderType.PDF,
            fullpage=True,
            scroll_control=ScrollMode.OFF,
            resolution="800x600",
            split=False,
        )
    markup.extend(
        [
            [
                InlineKeyboardButton(
                    text=f"Format - {_settings['render_type'].name.upper()}",
                    callback_data="format",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Page - {'Full' if _settings['fullpage'] else 'Partial'}",
                    callback_data="page",
                )
            ],
            [
                InlineKeyboardButton(
                    text=f"Scroll Site - {_settings['scroll_control'].value.title()}",
                    callback_data="scroll",
                )
            ],
        ]
    )
    _split = _settings["split"]
    _resolution = _settings["resolution"]
    if _split or "600" not in _resolution:
        markup.extend(
            [
                [InlineKeyboardButton(text="hide additional options ˄", callback_data="options")],
                [
                    InlineKeyboardButton(text=f"resolution | {_resolution}", callback_data="res"),
                ],
                [
                    InlineKeyboardButton(
                        text=f"Split - {'Yes' if _split else 'No'}",
                        callback_data="splits",
                    )
                ]
                if _settings["render_type"] != RenderType.PDF
                else [],
                [InlineKeyboardButton(text="▫️ site statitics ▫️", callback_data="statics")],
            ]
        )
    else:
        markup.append([InlineKeyboardButton(text="show additional options ˅", callback_data="options")])
    markup.extend(
        [
            [InlineKeyboardButton(text="▫️ start render ▫️", callback_data="render")],
            [InlineKeyboardButton(text="cancel", callback_data="cancel")],
        ]
    )
    await msg.edit(
        text="Choose the prefered settings",
        reply_markup=InlineKeyboardMarkup(markup),
    )


@WebshotBot.on_message(filters.command(["start"]))
async def start(_, message: Message) -> None:
    await message.reply_text(
        f"<b>Hi {message.from_user.first_name} 👋\n"
        "I can render website of a given link to either PDF or PNG/JPEG</b>",
        quote=True,
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("❓ About", callback_data="about_cb")]]),
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


@WebshotBot.on_message(filters.command(["support", "feedback", "help"]) & filters.private)
async def help_handler(_, message: Message) -> None:
    if Config.SUPPORT_GROUP_LINK is not None:
        await message.reply_text(
            "__Frequently Asked Questions__** : -\n\n"
            "A. How to use the bot to render a website?\n\n"
            "Ans:** Send the link of the website you want to render, "
            "choose the desired setting, and click `start render`.\n\n"
            "**B. How does this bot work?\n\n Ans:** This bot uses"
            " an actual browser under the hood to render websites.\n\n"
            "**C. How to report a bug or request a new feature?\n\n"
            "Ans:** For feature requests or bug reports, you can open an "
            "[issue](https://github.com/alenpaul2001/Web-Screenshot-Bot) in Github"
            " or send the inquiry message in the support group mentioned below.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(text="Support group", url=Config.SUPPORT_GROUP_LINK)]]
            ),
            disable_web_page_preview=True,
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
