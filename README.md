# Web-Screenshot-Bot
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/165cc3bc283f46879e0e0ed27abdc4a2)](https://www.codacy.com/gh/alenpaulvarghese/Web-Screenshot-Bot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alenpaulvarghese/Web-Screenshot-Bot&amp;utm_campaign=Badge_Grade)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![Try it on telegram](https://img.shields.io/badge/try%20it-on%20telegram-0088cc.svg)](http://t.me/BetterWebShotBot)

A Telegram _Web-Screenshot_ Bot Based on [Playwright](https://github.com/microsoft/playwright)
# Introduction

Telegram Bot that creates screenshot _PNG/JPEG_ or _PDF_ of a given link. Can be combined with a number of additional parameters, such as resolution, partial or full-page rendering. The bot is currently accessible through in @BetterWebShotBot.

### Available Resolutions are :
- <b>Image [PNG/JPEG]</b>
    - 800x600
    - 1280x720
    - 1920x1080
    - 2560x1440
- <b>PDF</b>
    - Letter
    - Legal
    - A4
    - A5

Splitting of long pages are available for png and jpeg.

# Installing 

> Note: the bot requires a Chromium browser binary to render websites.

## Docker (recommended)

The bundled image already ships a matching Chromium build, so there is nothing else to install:

```sh
git clone https://github.com/alenpaulvarghese/Web-Screenshot-Bot.git
cd Web-Screenshot-Bot
cp config.env.sample config.env   # then fill in your values
docker compose up -d
docker compose logs -f
```

Your Telegram session is stored in a named volume (`webshotbot-session`), so it survives
container rebuilds. Stop with `docker compose down`; add `-v` only if you want to log out and
authenticate again.

## Manual install

Requires Python 3.9+.

```sh
git clone https://github.com/alenpaulvarghese/Web-Screenshot-Bot.git
cd Web-Screenshot-Bot
python3 -m pip install -r requirements.txt
# Download the Chromium build that matches the pinned playwright version
playwright install chromium
# <Create config.env appropriately>
python3 __main__.py
```

> Use `playwright install chromium` (not `chrome`) — the bot launches the browser Chromium that
> ships with Playwright. Installing Chrome instead can cause a version mismatch at startup.

#### an example config.env 👇
```sh
BOT_TOKEN=12345:49dc3eeb1aehda3cI2TesHNHc
API_ID=256123
API_HASH=eb06d4abfb49dc3eeb1aeb98ae0f581e
### OPTIONAL ###
LOG_GROUP=-123990002
REQUEST_TIMEOUT=30
SUPPORT_GROUP=https://t.me/bytessupport
```

### Made with ❤️️ in Kerala
### Copyright & License 

* Copyright (C) 2023-2026 by [AlenPaulVarghese](https://github.com/alenpaulvarghese)
* Licensed under the terms of the [GNU AGPL Version 3.0](https://github.com/alenpaulvarghese/Web-Screenshot-Bot/blob/master/LICENSE)
