# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
from typing import List
import math
import io


# https://stackoverflow.com/questions/25705773/image-cropping-tool-python
def split_image(filename: Path) -> List[Path]:
    Image.MAX_IMAGE_PIXELS = None
    # https://coderwall.com/p/ovlnwa/use-python-and-pil-to-slice-an-image-vertically
    location_of_image = []
    img = Image.open(filename)
    width, height = img.size
    upper, left, count, slice_size = 0, 0, 1, 800
    slices = int(math.ceil(height / slice_size))
    for _ in range(slices):
        # if we are at the end, set the lower bound to be the bottom of the image
        if count == slices:
            lower = height
        else:
            lower = int(count * slice_size)
        bbox = (left, upper, width, lower)
        working_slice = img.crop(bbox)
        upper += slice_size
        # saving = the slice
        location_to_save_slice = (
            filename.parent / f"@Webs.ScreenCapture-{str(count)}{filename.suffix}"
        )
        working_slice.save(
            fp=location_to_save_slice, format=filename.suffix.removeprefix(".")
        )
        location_of_image.append(location_to_save_slice)
        count += 1
    img.close()
    return location_of_image


def draw_statics(name: str, metrics: dict) -> io.BytesIO:
    font_path = Path("assets", "fonts", "DMSans-Bold.ttf")
    font = ImageFont.truetype(font_path, size=1)
    font_size = 1
    # https://stackoverflow.com/a/4902713/13033981
    while font.getsize(name)[0] < 238.5:
        font_size += 1
        font = ImageFont.truetype(font=font_path, size=font_size)
    font_paper = Image.new("RGB", (265, 100), color="white")
    draw = ImageDraw.Draw(font_paper)
    w, h = font.getsize(name)
    draw.text(((265 - w) / 2, (100 - h) / 2), name, font=font, fill="black")
    main_paper = Image.open(Path("assets", "plain_paper.png"))
    main_paper.paste(font_paper, (800, 460, 1065, 560))
    font_paper.close()
    metrics_paper = "".join([f"{x} :- {y}\n" for x, y in metrics.items()])
    draw = ImageDraw.Draw(main_paper)
    font = ImageFont.truetype(font_path, size=28)
    draw.multiline_text((1185, 215), metrics_paper, fill="white", font=font, spacing=15)
    return_object = io.BytesIO()
    main_paper.save(
        return_object,
        format="png",
    )
    main_paper.close()
    return_object.name = "@Web-Screenshot.png"
    return return_object
