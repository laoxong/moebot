#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
import asyncio
import json
import logging
import os
import aiohttp

import telebot
import re
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv
load_dotenv()
from pyncm import apis as ncmapi

Bot_Token = os.getenv('Bot_Token')
UA = os.getenv('UA')

bot = AsyncTeleBot(Bot_Token)

# Configure logging
logging.basicConfig(format='%(asctime)s: %(levelname)s %(name)s | %(message)s',
                    level=logging.INFO)
logger = telebot.logger.setLevel(logging.DEBUG)

# Initialize the bot
bot = AsyncTeleBot(Bot_Token)

#异步请求HTTP
class arequests:
    async def gettext(url, UA=UA):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': UA}) as response:
                return await response.text()
    async def getfile(url):
        UA = 'MoeCbot/0.1 (+https://www.moec.top/bot/)'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': UA}) as response:
                return await response.read()
    async def getjson(url, UA=UA):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': UA}) as response:
                return await response.json()

async def fetch(url):
    UA = 'MoeCbot/0.1 (+https://www.moec.top/bot/)'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'User-Agent': UA}) as response:
            return await response()

# Handle '/start' and '/help'
@bot.message_handler(commands=['start'])
async def send_welcome(message):
    await bot.reply_to(message, "这是Moe Bot~~")

#网易云音乐获取
@bot.message_handler(commands=['ncm'])
async def ncm(message):
    #获取用户输入
    breakpoint()
    text = re.sub(' +', ' ', message.text)
    text = text.split(' ', 1)
    if len(text) == 2:
        name = text[1]
        res = await arequests.getjson("https://music.cyrilstudio.top/search?keywords={name}&limit=10".format(name=name), UA="Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 SE 2.X MetaSr 1.0")
        id = res['result']['songs'][0]['id']
        res = ncmapi.track.GetTrackAudio(id)
        if res["data"][0]["url"] != None:
            await bot.send_audio(message.chat.id, audio=res["data"][0]["url"], reply_to_message_id=message.message_id)
        else:
            await bot.send_message(message.chat.id, "获取失败或是VIP限制歌曲", reply_to_message_id=message.message_id)
    else:
        await bot.reply_to(message, "请输入歌曲名")

# 监听群组消息
@bot.message_handler(func=lambda message: True)
async def handel_all(message):
    #判断是否含有Pixiv链接
    if re.search(r'pixiv.net', message.text):
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

if __name__ == '__main__':
    asyncio.run(bot.polling())
