# -*- coding: utf-8 -*-
import config
import telebot
from telebot import apihelper,types
import cherrypy
import os


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
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        path = './download/{}/'.format(message.from_user.id)
        if not os.path.exists(path):
            os.makedirs(path)
        path += message.document.file_name
        with open(path, 'wb') as file:
           file.write(downloaded_file)
        bot.reply_to(message, "Принял Ваш файл!")
    except Exception as e:
        print(e)


@bot.message_handler(content_types=["text"])
def _(message):
    if message.text == "Загрузить бота":
        response = '''Загрузите файл в формате <i>*.zip</i> в котором должны содержаться следующие файлы:
- <code>requerements.txt</code>, в котором указаны зависимости вашего проекта
- <code>Procfile</code>, в котором указано, какой файл нам нужно запускать
<b>Важно! У нас установлен интерпретатор Python 3.5.2,
Позаботьтесь о совместимости Вашего кода!</b>'''
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row("Панель управления", "Загрузить бота")
        keyboard.row("О проекте")
        bot.send_message(message.chat.id, response, reply_markup=keyboard, parse_mode='html')
    else:
        response = 'Выберите интересующий Вас элемент меню:'
        keyboard = types.ReplyKeyboardMarkup(True, True)
        keyboard.row("Панель управления", "Загрузить бота")
        keyboard.row("О проекте")
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
        #Если нужно прокси (вписать свои)
        apihelper.proxy = PROXYLIST
        bot.polling(none_stop = True)
