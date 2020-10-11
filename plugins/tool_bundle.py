from pyppeteer import launch
from zipfile import ZipFile
from typing import List
from PIL import Image
import asyncio
import math
import io


class Printer(object):
    def __init__(self, _type: str):
        self.resolution = {'width': 800, 'height': 600}
        self.type = _type
        self.fullpage = True

    @property
    def arguments_to_print(self) -> dict:
        if self.type == "pdf":
            arguments_for_pdf = {
                'format': 'Letter', 'displayHeaderFooter': True,
                'margin': {"bottom": 70, "left": 25, "right": 35, "top": 40},
                "printBackground": True
            }
            if self.fullpage:
                arguments_for_pdf["pageRanges"] = "1-2"
            return arguments_for_pdf
        elif self.type == "png" or self.type == "jpeg":
            arguments_for_image = {
                'type': self.type, "omitBackground": True}
            if self.fullpage:
                arguments_for_image['fullPage'] = True
            return arguments_for_image


# https://stackoverflow.com/questions/25705773/image-cropping-tool-python
async def split_func(out: io.BytesIO, format: str) -> List[io.BytesIO]:
    Image.MAX_IMAGE_PIXELS = None
    # https://coderwall.com/p/ovlnwa/use-python-and-pil-to-slice-an-image-vertically
    location_of_image = []
    img = Image.open(out)
    width, height = img.size
    upper, left, count, slice_size = 0, 0, 1, 800
    slices = int(math.ceil(height/slice_size))
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
        if 'jpeg' in format:
            location_to_save_slice = f'@Webs.ScreenCapture-{str(count)}.jpeg'
        else:
            location_to_save_slice = f'@Webs.ScreenCapture-{str(count)}.png'
        split_out = io.BytesIO()
        split_out.name = location_to_save_slice
        working_slice.save(fp=split_out, format=format)
        location_of_image.append(split_out)
        count += 1
        await asyncio.sleep(0)
    out.close()
    return location_of_image


# https://stackoverflow.com/a/44946732/13033981
async def zipper(location_of_image: List[io.BytesIO]) -> io.BytesIO:
    zipped_file = io.BytesIO()
    with ZipFile(zipped_file, 'w') as zipper:
        for files in location_of_image:
            zipper.writestr(files.name, files.getvalue())
            files.close()
    zipped_file.name = "@Webs-Screenshot.zip"
    return zipped_file


async def screenshot_driver(link: str, tasks=[]) -> io.BytesIO:
    print('link: ', link)
    if len(tasks) != 0:
        print("yielded browser obj from existing task list:", link)
        browser = tasks[0]
    else:
        print(f"no browser obj in tasks, creating new... now getting {link}")
        browser = await launch(
            headless=False,
        )
        tasks.append(browser)
    page = await browser.newPage()
    await page.goto(link)
    await asyncio.sleep(5)
    # things to do
    print("Done!-", link)
    await page.close()
    if len(await browser.pages()) == 1:
        print('hm no one is using the browser, i am closing it: ', link)
        tasks.remove(browser)
        await browser.close()
    elif len(await browser.pages()) > 2:
        print("someone is using the broswer, i am leaving it there: ", link)
