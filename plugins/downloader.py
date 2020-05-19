# Thanks CWPROJECTS For Helping Me 
# Thanks Spechide For Supporting Me 
from pyrogram import Client,Filters,InlineKeyboardButton,InlineKeyboardMarkup
from plugins.slicer_tool import long_slice, text_message,blacklist
from pyppeteer import launch,errors
from PIL import Image
import asyncio
import time
import os 

try:
    EXEC_PATH = os.environ.get('GOOGLE_CHROME_SHIM')
except Exception as e:
    print('Driver Not Found')

async def mainer(link,path,is_image):
    browser = await launch(
        headless=True, 
        executablePath=EXEC_PATH
        )
    page = await browser.newPage()
    await page.goto(link)
    if is_image:
        await page.screenshot({'path': f'{path}','fullPage': True,'type':'png'})
    else:
        await page.pdf({'path':f'{path}',
        })
    await browser.close()
    
@Client.on_message(Filters.regex(pattern="http[s]*://.+") & Filters.private)
async def checker(client ,message):
    #https://t.me/Python/774464
    if [x for x in blacklist if x in message.text]:
        await message.reply_text("Please Dont Abuse This Service 😭😭") 
    else:
        msg = await message.reply_text("working", True)
        # Logger
        try:
		    LOGGING_GROUP = os.environ.get('LOG_GROUP')
		    await client.send_message(
		        chat_id=LOGGING_GROUP,
		        text=f"Request from {message.chat.first_name} aka @{message.chat.username}\n\nQuery : {message.text}",
		        disable_web_page_preview=True
		    )
        except Exception as e:
			print(f'Logging Avoided\nREASON : {e}')
			
        await msg.edit(text='Choose the prefered format',reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(text='PNG',callback_data=f'to_img')],
            [InlineKeyboardButton(text='PDF',callback_data=f'to_pdf')]
        ]))
			
@Client.on_callback_query()
async def cb_(client,callback_query):
    cb_data = callback_query.data
    msg = callback_query.message
    if not os.path.isdir('./FILES/'):
            os.mkdir('./FILES/')
    tmp_dir = './FILES/' + str(callback_query.message.chat.id) + "/"
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)
    
    #https://medium.com/@epicshane/one-liner-for-python-if-elif-else-statements-d9d46016ba2a
    file = {cb_data=='to_img': tmp_dir+"image.png",cb_data=='to_pdf': tmp_dir+'image.pdf'}.get(True, tmp_dir+"image.png")
    

    if cb_data == "to_img" or cb_data == "to_pdf":
        url = callback_query.message.reply_to_message.text 
        mode = True if cb_data == "to_img" else False
        await msg.edit('Trying to Render...')
        #Main Function
        try:
            await mainer(url,file,mode)
        except errors.PageError as e:
            await msg.edit(text='Not a valid link 😓🤔')
            return False
        await msg.edit('Succefully Rendered')
        if cb_data == "to_img":         
            dimension = Image.open(file)
            width,height = dimension.size
            await asyncio.sleep(3)
            await msg.edit(text=f'**Image Description**\nwidth  : {width}\nheight : {height}')
            await asyncio.sleep(2.5)
            if height > 4000:           
                await msg.reply_text(text=text_message,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton(text='yes',callback_data='split')],
                        [InlineKeyboardButton(text='no',callback_data='dont_split')]
                    ])
                  )
                return

        await msg.edit('Uploading...')
        await client.send_document(
            document=file,
            chat_id=callback_query.message.chat.id
        )
        await msg.delete()
        os.remove(file)


    elif cb_data == "split" or cb_data == "dont_split":
        if cb_data == "dont_split":
            await msg.edit('Uploading...')
            await client.send_document(
                document=file,
                chat_id=callback_query.message.chat.id
            )
            os.remove(file)
        else:
            id_of_the_chat = callback_query.message.chat.id
            await msg.edit("uploading")
            await long_slice(file,str(id_of_the_chat),id_of_the_chat,client)
        await msg.delete()
        
