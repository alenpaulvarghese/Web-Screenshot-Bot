# Web-Screenshot-Bot
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/165cc3bc283f46879e0e0ed27abdc4a2)](https://www.codacy.com/gh/alenpaul2001/Web-Screenshot-Bot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alenpaul2001/Web-Screenshot-Bot&amp;utm_campaign=Badge_Grade)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![Try it on telegram](https://img.shields.io/badge/try%20it-on%20telegram-0088cc.svg)](http://t.me/BetterWebShotBot)

A Telegram _Web-Screenshot_ Bot Based on Pyrogram
# Introduction

Telegram Bot that creates screenshot _[PNG/JPEG]_ or PDF of a given link. Can be matched with various other settings like resolution, partial or full-page rendering. The bot can currently be found in @BetterWebShotBot.

### Available Resolutions are :

1. 800x600
2. 1280x720
3. 1920x1080
4. 2560x1440

Splitting of long pages are available for png and jpeg.

# Installing 

> Note: the bot requires chromium/chrome binary to render websites.
### <b>The Legacy Way</b>
Simply clone the repository and run the main file:

```sh
git clone https://github.com/alenpaul2001/Web-Screenshot-Bot.git
cd Web-Screenshot-Bot
python -m pip install poetry
poetry install --no-dev && poetry shell
# <Create config.env appropriately>
python3 __main__.py
```
#### an example config.env 👇
```sh
BOT_TOKEN=12345:49dc3eeb1aehda3cI2TesHNHc
API_ID=256123
API_HASH=eb06d4abfb49dc3eeb1aeb98ae0f581e
### CHROME EXEC PATH ? LEAVE THIS BLANK ###
GOOGLE_CHROME_SHIM=
### OPTIONAL ###
LOG_GROUP=-123990002
SUPPORT_GROUP_LINK=https://t.me/bytessupport
```


# Thanks to

[Dan Tès](https://telegram.dog/haskell) for his [Pyrogram Library](https://github.com/pyrogram/pyrogram)

[Mattwmaster58](https://github.com/Mattwmaster58) for the port of [Pyppeteer Library](https://github.com/pyppeteer/pyppeteer)

### special thanks to :

[<\-W4RR10R-/>](https://github.com/CW4RR10R) and [@SpEcHIDe](https://github.com/SpEcHiDe) for helping me.

[Λиʞ⫯𝚝⅁øμϩᴧ⋎](https://github.com/Ankit-Gourav) and 
[//𝚂𝚊𝚢𝚊𝚗𝚝𝚑//](https://github.com/SayanthD) for suggesting new features.

### Made with ❤️️ in Kerala
### Copyright & License 

* Copyright (C) 2021 by [AlenPaulVarghese](https://github.com/alenpaul2001)
* Licensed under the terms of the [GNU AGPL Version 3.0](https://github.com/alenpaul2001/Web-Screenshot-Bot/blob/master/LICENSE)
