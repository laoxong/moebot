#!/usr/bin/python

# This is a simple echo bot using the decorator mechanism.
# It echoes any incoming text messages.
import asyncio
import logging
import sqlite3
import os
from tkinter import N
from tkinter.messagebox import NO
import aiohttp

import telebot
import re
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv
load_dotenv()

Bot_Token = os.getenv('Bot_Token')
bot = AsyncTeleBot(Bot_Token)

# Configure logging
logging.basicConfig(format='%(asctime)s: %(levelname)s %(name)s | %(message)s',
                    level=logging.INFO)

logger = telebot.logger.setLevel(logging.INFO)

# Initialize the bot
bot = AsyncTeleBot(Bot_Token)

#异步请求HTTP
class arequests:
    async def gettext(url):
        '''
        异步请求HTTP
        '''
        UA = 'MoeCbot/0.1 (+https://www.moec.top/bot/)'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': UA}) as response:
                return await response.text()
    async def getfile(url):
        '''
        异步请求HTTP
        '''
        UA = 'MoeCbot/0.1 (+https://www.moec.top/bot/)'
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers={'User-Agent': UA}) as response:
                return await response.read()


async def fetch(url):
    UA = 'MoeCbot/0.1 (+https://www.moec.top/bot/)'
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'User-Agent': UA}) as response:
            return await response()

# Handle '/start' and '/help'
@bot.message_handler(commands=['start', 'help'])
async def send_welcome(message):
    await bot.reply_to(message, "Howdy, how are you doing?")

# 监听所有消息
@bot.message_handler()
async def echo_all(message):
    #判断是否含有Pixiv链接
    if re.search(r'pixiv.net', message.text):
        #获取Pixiv链接
        breakpoint()
        pixiv_url = re.search(r'(https?://[^\s]+)', message.text).group(1)
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




asyncio.run(bot.polling())