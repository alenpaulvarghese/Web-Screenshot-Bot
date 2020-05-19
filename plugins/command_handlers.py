from pyrogram import Client,Filters
import asyncio

@Client.on_message(Filters.command(["start"]))
async def start(client,message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Please Send Any Link",
        reply_to_message_id=message.message_id
    )

@Client.on_message(Filters.command(["feedback"]))
async def feedback(client,message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"for suggetions and feedbacks contact @STARKTM1",
        reply_to_message_id=message.message_id
    )

@Client.on_message(Filters.command(["about"]))
async def about(client,message):
    await client.send_message(
        chat_id=message.chat.id,
        text='This bot is created by @StarkTM1 as a project\n\n Thanks to <a href="https://t.me/cwprojects">@W4RR10R</a> and <a href="https://t.me/SpEcHlDe">@SpEcHIDe</a> for helping me ',
        disable_web_page_preview=True
    )

@Client.on_message(Filters.command(["notworking"]))
async def notworking(client,message):
    await client.send_message(
        chat_id=message.chat.id,
        text=f"Make sure Your Request has http or https prefix",
        reply_to_message_id=message.message_id
    )