# -*- coding: utf-8 -*-
import telebot
from telebot import apihelper
import os
import sys
import backend
from backend import SQLighter
from backend import config

TOKEN = config.token
PROXYLIST = config.proxy
DB = config.db

bot = telebot.TeleBot(TOKEN)


def main(arg):
    bot_id = arg[1]
    db = SQLighter(DB)
    ent = db.get_bot(bot_id)
    if ent:
        user_id = ent[4]
        db.update_bot(bot_id, status=0)
        response = f'Бот {bot_id} был остановлен'
        bot.send_message(user_id, response)


if __name__ == '__main__':
    if PROXYLIST:
        apihelper.proxy = PROXYLIST
    main(sys.argv)
