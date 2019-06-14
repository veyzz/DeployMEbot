# -*- coding: utf-8 -*-
import config
import telebot
from telebot import apihelper, types
import cherrypy
import os
import zipfile
import json
import re
import time
from backend import preparefiles
from dmbhelper import SQLighter


MODE = config.mode
TOKEN = config.token
PROXYLIST = config.proxy
DB = config.db
BOTS_COUNT = config.bots_count


bot = telebot.TeleBot(TOKEN)


class WebhookServer:

    @cherrypy.expose
    def index(self):
        length = int(cherrypy.request.headers['content-length'])
        json_string = cherrypy.request.body.read(length).decode("utf-8")
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''


@bot.message_handler(commands=['start', 'help'])
def _(message):
    response = '''Привет! Этот бот позволяет развернуть Вашего бота
на сервере, чтобы держать его запущенным 24/7.'''
    keyboard = types.ReplyKeyboardMarkup(True, True)
    keyboard.row('Попробовать')
    bot.send_message(message.chat.id, response, reply_markup=keyboard)
    db = SQLighter(DB)
    if not db.get_user(message.from_user.id):
        db.insert_user(message.from_user.id)


@bot.message_handler(content_types=['document'])
def _(message):
    try:
        user_id = message.from_user.id
        file_name = re.sub(r'[^A-z0-9\.]', '', message.document.file_name)
        bot_name, _ = os.path.splitext(file_name)
        downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)
        if message.document.mime_type != "application/zip":
            bot.reply_to(message, "Файл должен быть формата zip!")
            return
        path = './download/{}/'.format(user_id)
        if not os.path.exists(path):
            os.makedirs(path)
        path += file_name
        path = os.path.abspath(path)
        with open(path, 'wb') as file:
            file.write(downloaded_file)
        with zipfile.ZipFile(path, 'r') as z:
            files = z.namelist()
        req = False
        st = False
        for element in files:
            if 'requirements.txt' in element:
                req = True
            if 'tostart.txt' in element:
                st = True
        if not req:
            bot.reply_to(message, "Вы забыли файл requirements.txt")
        if not st:
            bot.reply_to(message, "Вы забыли файл tostart.txt")
        if not (req and st):
            os.remove(path)
            return
        db = SQLighter(DB)
        bots = db.get_bots(user_id)
        exist = False
        for item in bots:
            if bot_name in item:
                db.update_bot(item[0], status=False)
                exist = True
        if not exist:
            bot_id = int(time.time())
            db.insert_bot(bot_id, bot_name, False, 0, user_id)
        preparefiles.deploy(user_id, file_name, os.getcwd())
        bot.reply_to(message, "Файл принят!")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка... Попробуйте еще раз.")
        if not db.get_user(message.from_user.id):
            db.insert_user(message.from_user.id)
        print("error: ", e)


@bot.message_handler(content_types=["text"])
def _(message):
    if message.text == "⬇️ Загрузить бота":
        response = '''Загрузите файл в формате <i>*.zip</i> в котором должны содержаться следующие файлы:
- <code>requerements.txt</code>, в котором указаны зависимости вашего проекта
- <code>tostart.txt</code>, в котором указано, какой файл нам нужно запускать
<b>Важно! У нас установлен интерпретатор Python 3.5.2,
Позаботьтесь о совместимости Вашего кода!</b>'''
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("💬 О проекте")
        bot.send_message(message.chat.id, response,
                         reply_markup=keyboard, parse_mode='html')
    elif message.text == "🔐 Панель управления":
        response = "Панель управления"
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row("🚀 Запуск/остановка", "🧩 Обновить файлы")
        keyboard.row("💬 Посмотреть логи")
        bot.send_message(message.chat.id, response, reply_markup=keyboard)
    else:
        response = 'Выберите интересующий Вас элемент меню:'
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("💬 О проекте")
        bot.send_message(message.chat.id, response, reply_markup=keyboard)


if __name__ == '__main__':
    if MODE == 1:
        cherrypy.config.update({
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 7777,
            'engine.autoreload.on': True
        })
        cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
    elif MODE == 0:
        # Если нужно прокси (вписать свои)
        apihelper.proxy = PROXYLIST
        bot.polling(none_stop=True)
