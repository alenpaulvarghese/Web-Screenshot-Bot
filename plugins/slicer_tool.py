# https://coderwall.com/p/ovlnwa/use-python-and-pil-to-slice-an-image-vertically
from __future__ import division
from pyrogram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from PIL import Image
import math
import asyncio

blacklist = ['drive.google.com', 'tor.checker.in']
HOME = InlineKeyboardMarkup([
            [InlineKeyboardButton(text='Format - PDF', callback_data='format')],
            [InlineKeyboardButton(text='Page - Full', callback_data="page")],
            # [InlineKeyboardButton(text='Landscape', callback_data="orientation")],
            [InlineKeyboardButton(text='show additional options ˅', callback_data="options")],
            [InlineKeyboardButton(text='▫️ start render ▫️', callback_data="render")],
            [InlineKeyboardButton(text='cancel', callback_data="cancel")]
                            ])


async def long_slice(image_path, location, format):
    slice_size = 800
    """slice an image into parts slice_size tall"""
    img = Image.open(image_path)
    width, height = img.size
    upper = 0
    left = 0
    slices = int(math.ceil(height/slice_size))
    count = 1
    location_to_save = []
    for slice in range(slices):
        # if we are at the end, set the lower bound to be the bottom of the image
        if count == slices:
            lower = height
        else:
            lower = int(count * slice_size)
        bbox = (left, upper, width, lower)
        working_slice = img.crop(bbox)
        upper += slice_size
        # save the slice
        if 'jpeg' in format:
            location_to_save_slice = f'{location}/slice_{str(count)}.jpeg'
        else:
            location_to_save_slice = f'{location}/slice_{str(count)}.png'
        location_to_save.append(InputMediaPhoto(
            media=location_to_save_slice,
            caption=str(count)
            ))
        working_slice.save(location_to_save_slice)
        count += 1
    return location_to_save
