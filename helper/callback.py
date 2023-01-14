from typing import Callable

from helper.printer import RenderType


def get_resolution(current_res: str, render_type: RenderType):
    """Return the next resolution from the given one."""
    image_resolutions = [
        "800x600",
        "1280x720",
        "1920x1080",
        "2560x1440",
    ]
    pdf_resolutions = [
        "Letter",
        "Legal",
        "A4",
        "A5",
    ]
    resolutions = pdf_resolutions if render_type == RenderType.PDF else image_resolutions
    current_index = resolutions.index(current_res)
    # If the current index is the last element of the list the index will be reset to 0.
    return resolutions[(current_index + 1) % len(resolutions)]


def extract_render_type(fn: Callable):
    """
    Decorator function that lookups the first button of the `CallbackQuery`
    message object, find the `RenderType` and pass that on the the child function.
    """

    async def wrapper(*args, **kwargs):
        callback = args[-1]
        current_format: str = callback.message.reply_markup.inline_keyboard[0][0].text
        current_format = current_format.removeprefix("Format - ").lower()
        render_type = RenderType(current_format)
        await fn(*args, **kwargs, render_type=render_type)

    return wrapper
