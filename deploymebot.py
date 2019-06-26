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
import random
import backend
from dmbhelper import SQLighter
import proxy

MODE = config.mode
TOKEN = config.token
PROXYLIST = proxy.proxy
DB = config.db
BOTS_COUNT = config.bots_count
COMMANDS = config.commands
PATH = os.getcwd()
EPOCH = config.epoch

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
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.row('✨Попробовать✨')
    bot.send_message(message.chat.id, response, reply_markup=keyboard)
    db = SQLighter(DB)
    if not db.get_user(message.from_user.id):
        if re.search('/start (\w+)', message.text):
            ref = re.search('/start (\w+)', message.text).group(1)
            user = db.get_ref(ref)
            if user:
                db.insert_user(message.from_user.id, user[0])
                db.update_user(user[0], ref_count=user[3] + 1)
                try:
                    response = "Похоже, кто-то пришел к нам по вашей ссылке. Спасибо."
                    bot.send_message(user[0], response)
                except Exception as e:
                    print(e)
    if not db.get_user(message.from_user.id):
        db.insert_user(message.from_user.id)


@bot.message_handler(content_types=['document'])
def _(message):
    mes = None
    try:
        mes = bot.reply_to(message, "Обрабатываем...")
        user_id = message.from_user.id
        file_name = re.sub(r'[^A-z0-9\.]', '', message.document.file_name)
        bot_name, _ = os.path.splitext(file_name)
        downloaded_file = bot.download_file(
            bot.get_file(message.document.file_id).file_path)
        if message.document.mime_type != "application/zip":
            bot.edit_message_text("Файл должен быть формата zip!", mes.chat.id,
                                  mes.message_id)
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
        err = ""
        if not req:
            err += "Вы забыли файл requirements.txt\n"
        if not st:
            err += "Вы забыли файл tostart.txt\n"
        if not (req and st):
            os.remove(path)
            bot.edit_message_text(err, mes.chat.id, mes.message_id)
            return
        db = SQLighter(DB)
        bots = db.get_bots(user_id)
        exist = False
        for item in bots:
            if bot_name in item:
                db.update_bot(item[0], status=False)
                exist = True
        if not exist:
            bot_id = backend.get_hash(user_id) + backend.get_hash(
                int(time.time() - EPOCH))
            db.insert_bot(bot_id, bot_name, False, 0, user_id)
        backend.deploy(user_id, file_name)
        bot.edit_message_text("Файл принят!", mes.chat.id, mes.message_id)
    except Exception as e:
        if mes:
            bot.edit_message_text("Произошла ошибка... Попробуйте еще раз.",
                                  mes.chat.id, mes.message_id)
        else:
            bot.reply_to(message, "Произошла ошибка... Попробуйте еще раз.")
        if not db.get_user(message.from_user.id):
            db.insert_user(message.from_user.id)
        print("error: ", e)


@bot.message_handler(regexp='/bot_(\w+) (\w+)')
def _(message):
    if re.search('/bot_(\w+) (\w+)', message.text):
        reg = re.search('/bot_(\w+) (\w+)', message.text)
        command = reg.group(1)
        bot_id = reg.group(2)
        if command in COMMANDS:
            db = SQLighter(DB)
            bots = db.get_bots(message.from_user.id)
            bot_name = ''
            for item in bots:
                if str(item[0]) == bot_id:
                    bot_name = item[1]
                    break
            if bot_name:
                backend.controlbot(bot_id, command)
            else:
                response = "<i>Нет такого бота...</i>"
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                     row_width=3)
                keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
                keyboard.row("💻 О проекте")
                bot.send_message(message.chat.id,
                                 response,
                                 reply_markup=keyboard,
                                 parse_mode='html')
        else:
            response = "<i>Forbidden</i>"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                 row_width=3)
            keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
            keyboard.row("💻 О проекте")
            bot.send_message(message.chat.id,
                             response,
                             reply_markup=keyboard,
                             parse_mode='html')


@bot.message_handler(content_types=["text"])
def _(message):
    if message.text == "⬇️ Загрузить бота":
        response = '''Загрузите файл в формате <i>*.zip</i> в котором должны содержаться следующие файлы:
- <code>requerements.txt</code>, в котором указаны зависимости вашего проекта
- <code>tostart.txt</code>, в котором указано, какой файл нам нужно запускать
<b>Важно! У нас установлен интерпретатор Python 3.5.2,
Позаботьтесь о совместимости Вашего кода!</b>'''
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "🔐 Панель управления":
        db = SQLighter(DB)
        bots = db.get_bots(message.from_user.id)
        response = ""
        for item in bots:
            try:
                if backend.check_status(item[0]):
                    status = "Запущен"
                else:
                    status = "Выключен"
            except:
                status = "Неизвестно"
            response += """
<b>{}</b> [<i>{}</i>]
ID бота: <code>{}</code>
Осталось времени: <i>{}</i>\n""".format(item[1], status, item[0], item[3])
        if not response:
            response = "\n<i>Пусто...</i>"
        response = "Ваши боты:\n" + response
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "🚀 Запуск/остановка":
        response = """Управление ботом:

Запустить - /bot_start {id}
Остановить - /bot_stop {id}
"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "🧩 Обновить файлы":
        response = "Обновить файлы"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "💥 Удалить бота":
        response = """Удалить бота

/bot_remove {id}

<b>Внимание! После отправки команды бот окончательно будет удален.</b>"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "💬 Посмотреть логи":
        response = "Посмотреть логи:\n\n/bot_logs {id}"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "💻 О проекте":
        response = 'О проекте'
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("💻 О проекте")
        bot.send_message(message.chat.id, response, reply_markup=keyboard)
    else:
        response = 'Выберите интересующий Вас элемент меню:'
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("💻 О проекте")
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
        # Если нужно прокси (вписать свои) в файл proxy.py
        if PROXYLIST:
            apihelper.proxy = PROXYLIST
        bot.polling(none_stop=True)
