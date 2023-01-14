# (c) AlenPaulVarghese
# -*- coding: utf-8 -*-

import math
from pathlib import Path
from typing import List

from PIL import Image


# https://stackoverflow.com/questions/25705773/image-cropping-tool-python
def split_image(filename: Path) -> List[Path]:
    """Function to split image vertically."""
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
        location_to_save_slice = filename.parent / f"@Webs.ScreenCapture-{str(count)}{filename.suffix}"
        working_slice.save(fp=location_to_save_slice, format=filename.suffix.removeprefix("."))
        location_of_image.append(location_to_save_slice)
        count += 1
    img.close()
    return location_of_image
