# -*- coding: utf-8 -*-
import config
import telebot
from telebot import apihelper, types
import cherrypy
import os
import zipfile
from backend import preparefiles


MODE = config.mode
TOKEN = config.token
PROXYLIST = config.proxy


bot = telebot.TeleBot(TOKEN)


class WebhookServer(object):
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


@bot.message_handler(content_types=['document'])
def _(message):
    try:
        downloaded_file = bot.download_file(bot.get_file(message.document.file_id).file_path)
        if message.document.mime_type != "application/zip":
            bot.reply_to(message, "Файл должен быть формата zip!")
            return
        path = './download/{}/'.format(message.from_user.id)
        if not os.path.exists(path):
            os.makedirs(path)
        path += message.document.file_name
        path = os.path.abspath(path)
        with open(path, 'wb') as file:
            file.write(downloaded_file)
        with zipfile.ZipFile(path, 'r') as z:
            files = z.namelist()
        flag = False
        for element in files:
            if 'requirements.txt' in element:
                flag = True
        if not flag:
            bot.reply_to(message, "Вы забыли файл requirements.txt")
            os.remove(path)
            return
        bot.reply_to(message, "Файл принят!")
        preparefiles.deploy(message.from_user.id, path, os.getcwd())
        os.remove(path)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка... Попробуйте еще раз.")
        print(e)


@bot.message_handler(content_types=["text"])
def _(message):
    if message.text == "⬇️ Загрузить бота":
        response = '''Загрузите файл в формате <i>*.zip</i> в котором должны содержаться следующие файлы:
- <code>requerements.txt</code>, в котором указаны зависимости вашего проекта
- <code>Procfile</code>, в котором указано, какой файл нам нужно запускать
<b>Важно! У нас установлен интерпретатор Python 3.5.2,
Позаботьтесь о совместимости Вашего кода!</b>'''
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("💬 О проекте")
        bot.send_message(message.chat.id, response,
                         reply_markup=keyboard, parse_mode='html')
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
