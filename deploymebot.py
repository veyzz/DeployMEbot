# -*- coding: utf-8 -*-
import config
import telebot
from telebot import apihelper,types
import cherrypy


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


@bot.message_handler(commands=['help'])
def _(message):
    response = 'Помощи пока нет'
    bot.send_message(message.chat.id, response)


@bot.message_handler(content_types=["text"])
def _(message):
    response = 'Любое сообщение'
    bot.send_message(message.chat.id, response)

        
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