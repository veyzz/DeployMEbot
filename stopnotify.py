# -*- coding: utf-8 -*-
import config
import telebot
from telebot import apihelper
import os
import backend
from dmbhelper import SQLighter
import proxy
import sys

TOKEN = config.token
PROXYLIST = proxy.proxy
DB = config.db

bot = telebot.TeleBot(TOKEN)


def main(arg):
    bot_id = arg[1]
    db = SQLighter(DB)
    ent = db.get_bot(bot_id)
    user_id = ent[4]
    db.update_bot(bot_id, status=0)
    response = 'Бот {} был остановлен'.format(bot_id)
    bot.send_message(user_id, response)


if __name__ == '__main__':
    if PROXYLIST:
        apihelper.proxy = PROXYLIST
    main(sys.argv)
