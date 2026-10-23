

# Web-Screenshot-Bot
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/165cc3bc283f46879e0e0ed27abdc4a2)](https://www.codacy.com/gh/alenpaul2001/Web-Screenshot-Bot/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=alenpaul2001/Web-Screenshot-Bot&amp;utm_campaign=Badge_Grade)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/) [![Open Source Love svg1](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
[![Try it on telegram](https://img.shields.io/badge/try%20it-on%20telegram-0088cc.svg)](http://t.me/BetterWebShotBot)

Un bot de Telegram _Web-Screenshot_ basado en [Playwright](https://github.com/microsoft/playwright)
# Introducción

Bot de Telegram que crea capturas de pantalla _PNG/JPEG_ o _PDF_ de un enlace dado. Se puede combinar con una serie de parámetros adicionales, como resolución, renderizado parcial o de página completa. Actualmente, el bot es accesible a través de @BetterWebShotBot.

### Las resoluciones disponibles son:
- <b>Imagen [PNG/JPEG]</b>
    - 800x600
    - 1280x720
    - 1920x1080
    - 2560x1440
- <b>PDF</b>
    - Letter
    - Legal
    - A4
    - A5

La división de páginas largas está disponible para PNG y JPEG.

# Instalación 

> Nota: el bot requiere el binario de chromium/chrome para renderizar los sitios web.
Simplemente clona el repositorio y ejecuta el archivo principal:

```sh
git clone https://github.com/alenpaul2001/Web-Screenshot-Bot.git
cd Web-Screenshot-Bot
python -m pip install poetry
poetry install --no-dev && poetry shell
# Install chrome if you don't have it in your system
playwright install chrome
# <Create config.env appropriately>
python3 __main__.py
```
#### Un ejemplo de config.env 👇
```sh
BOT_TOKEN=12345:49dc3eeb1aehda3cI2TesHNHc
API_ID=256123
API_HASH=eb06d4abfb49dc3eeb1aeb98ae0f581e
### OPTIONAL ###
LOG_GROUP=-123990002
SUPPORT_GROUP_LINK=https://t.me/bytessupport
```

### Hecho con ❤️️ en Kerala
### Copyright y Licencia 

* Copyright (C) 2023 por [AlenPaulVarghese](https://github.com/alenpaul2001)
* Licenciado bajo los términos de la [GNU AGPL Versión 3.0](https://github.com/alenpaul2001/Web-Screenshot-Bot/blob/master/LICENSE)
