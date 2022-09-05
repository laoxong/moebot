#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
import asyncio
from email import message
import json
import logging
import os
import aiohttp
import sys
import time

import telebot
import aiomysql
import re
from telebot.async_telebot import AsyncTeleBot
from utils.dom import *
#加载配置文件
from dotenv import load_dotenv
load_dotenv()
Bot_Token = os.getenv('Bot_Token')
UA = os.getenv('UA')
telegraph_token = os.getenv('telegraph_token')

# Configure logging
logging.basicConfig(format='%(asctime)s: %(levelname)s %(name)s | %(message)s',
                    level=logging.INFO)

# Initialize
# if "-init" in sys.argv[1::]:
#     logging.info("Initializing database...")
#     # Initialize database
#     logging.info("Database initialized.")
# logging.info("Initializing bot...")
bot = AsyncTeleBot(Bot_Token)


# Handle '/help'
@bot.message_handler(commands=['help'])
async def send_welcome(message):
    await bot.reply_to(message, """
    这是Moe Bot~~
    """)


#上传图片到Telegraph
@bot.message_handler(commands=['updatetotelegraph'])
async def telegraph_upload(message):
    if message.reply_to_message != None:
        #下载图片
        day = str(time.strftime("%d", time.localtime()))
        month = str(time.strftime("%m", time.localtime()))
        file_id = message.reply_to_message.photo[-1].file_id
        file_info = await bot.get_file(file_id)
        file = await arequests.getfile('https://api.telegram.org/file/bot{0}/{1}'.format(Bot_Token, file_info.file_path))
        img = await telegraph.upload(file)
        path = str(message.from_user.id) + "-" + str(day) + "-" +str(month)
        content = await telegraph.getpage(path)
        text = ""
        if content["ok"] == True:
            text = content["result"]["content"].append({'tag': 'figure', 'children': [{'tag': 'img', 'attrs': {'src': f'{photsupdated[0]}'}}, {'tag': 'figcaption', 'children': ['']}]})
            res = await telegraph.editpage(content["result"]["path"], f"{message.from_user.id}-{day}-{month}", message.from_user.full_name, text)
        else:
            #上传图片到Telegraph
            res = await telegraph.create(message.from_user.id , message.from_user.full_name, message.reply_to_message.text,images=img[0]['src'])
        if res["ok"] == True:
            await bot.reply_to(message , f"""
            上传成功
            地址： {res['result']['url']}
            """)
        else:
            await bot.reply_to(message , f"""
            上传失败
            """)
    else:
        await bot.reply_to(message , "请回复一张图片")

# 监听群组消息
@bot.message_handler(func=lambda message: True)
async def handel_all(message):
    #判断是否含有Pixiv链接
    if re.search(r'pixiv.net/artworks', message.text):
        pixiv_url = re.search(r'(https?://[^\s]+)', message.text).group(1)
        await pixiv_url_handle(pixiv_url, message)

#提取指令
async def getinput(message, num):
    #获取用户输入
    text = re.sub(' +', ' ', message.text)
    text = text.split(' ')
    if len(text) == num+1:
        return text
    else:
        return False

#异步请求HTTP
class arequests:
    async def gettext(url, UA=UA, params=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': UA}, params=params) as response:
                return await response.text()
    async def getfile(url, UA=UA, params=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': UA}, params=params) as response:
                return await response.read()
    async def getjson(url, UA=UA, params=None):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': UA}, params=params) as response:
                return await response.json()
    async def postjson(url, data, UA=UA):
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=data, headers={'User-Agent': UA}) as response:
                return await response.json()
#Pixiv链接处理
async def pixiv_url_handle(pixiv_url, message):
    #获取Pixiv
    text = await arequests.gettext(pixiv_url)
    #获取Pixiv标题
    try:
        title = re.search(r'<meta property="og:title" content="(.+?)">', text).group(1)
    except:
        title = '获取失败'
    #获取简介
    try:
        description = re.search(r'<meta name="description" content="(.+?)">', text).group(1)
    except:
        description = '获取失败'
    #获取Pixiv作者
    try:
        author = re.search(r'<meta property="og:description" content="(.+?)">', text).group(1)
    except:
        author = '获取失败'
    #获取Pixiv图片
    img_url = re.search(r'<meta property="og:image" content="(.+?)">', text).group(1)
    # 发送Pixiv信息和Pixiv图片
    await bot.send_photo(message.chat.id, photo=img_url, caption=f'标题：{title}\n作者：{author}\n简介：{description}\n链接：{pixiv_url}', 
    reply_to_message_id=message.message_id)

#Telegraph
class telegraph:
    async def upload(file):
        url = 'https://telegra.ph/upload'
        data = {'file': file}
        return await arequests.postjson(url, data, UA=UA)
    async def create(title, author , text, images):
        url = 'https://api.telegra.ph/createPage'
        
        text = """
        <img src="{images}">
        """.format(images=images)
        content_json = json_dumps(html_to_nodes(text))
        data = {
            'access_token': telegraph_token,
            'title': title,
            'author_name': author,
            'content': content_json
        }
        return await arequests.getjson(url, UA=UA, params=data)
    async def getpage(path, return_content="False"):
        url = 'https://api.telegra.ph/getPage'
        data = {
            'path': path,
            'return_content': return_content
        }
        return await arequests.getjson(url, UA=UA, params=data)
    async def editpage(path, title, author, content, return_content="False"):
        url = 'https://api.telegra.ph/editPage'
        data = {
            'access_token': telegraph_token,
            'path': path,
            'title': title,
            'author_name': author,
            'content': json.loads(content),
            'return_content': return_content
        }
        return await arequests.getjson(url, UA=UA, params=data)

if __name__ == '__main__':
    asyncio.run(bot.polling())
