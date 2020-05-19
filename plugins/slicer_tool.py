#https://coderwall.com/p/ovlnwa/use-python-and-pil-to-slice-an-image-vertically
from __future__ import division
from PIL import Image
import math
import os
import asyncio

text_message = "**Note**:\nFor Smart-phone users, the rendered image cannot be viewed properly if the height is above 4000\n\nDo u want to split the file?"

blacklist = ['drive.google.com','tor.checker.in']

async def long_slice(image_path, out_name,id_of_the_chat,client):
    slice_size = 4500
    outdir='./FILES'
    """slice an image into parts slice_size tall"""
    img = Image.open(image_path)
    width, height = img.size
    upper = 0
    left = 0
    slices = int(math.ceil(height/slice_size))

    count = 1
    for slice in range(slices):
        #if we are at the end, set the lower bound to be the bottom of the image
        if count == slices:
            lower = height
        else:
            lower = int(count * slice_size)  

        bbox = (left, upper, width, lower)
        working_slice = img.crop(bbox)
        upper += slice_size
        #save the slice
        location = os.path.join(outdir, "slice_" + out_name + "_" + str(count)+".png")
        working_slice.save(location)
        await client.send_document(
                document=location,
                chat_id=id_of_the_chat
            )
        os.remove(location)
        count +=1
    #await 
