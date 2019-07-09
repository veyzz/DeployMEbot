# -*- coding: utf-8 -*-
import json
import os
import random
import re
import time
import zipfile
import cherrypy
import telebot
from telebot import apihelper, types
import backend
from backend import config
from backend import SQLighter

MODE = config.mode
TOKEN = config.token
PROXYLIST = config.proxy
DB = config.db
BOTS_COUNT = config.bots_count
COMMANDS = config.commands
PATH = os.getcwd()
EPOCH = config.epoch
FEEDBACK = config.feedback_channel

bot = telebot.TeleBot(TOKEN)
logger = backend.get_logger('Main', f'{PATH}/log/deploymebot.log')
logger.info('DeployMeBot started')


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
    response = \
"Этот бот позволяет развернуть Вашего бота \
на сервере, чтобы держать его запущенным 24/7. \
\nДля связи: <code>/feedback {сообщение}</code>"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.row('✨Попробовать✨')
    bot.send_message(message.chat.id,
                     response,
                     reply_markup=keyboard,
                     parse_mode='html')
    db = SQLighter(DB)
    if not db.get_user(message.from_user.id):
        if re.search('/start (\w+)', message.text):
            ref = re.search('/start (\w+)', message.text).group(1)
            user = db.get_ref(ref)
            if user:
                db.insert_user(message.from_user.id, user[0])
                db.update_user(user[0], ref_count=user[3] + 1)
                logger.info(f"{user[0]} invited {message.from_user.id}")
                try:
                    response = "Похоже, кто-то пришел к нам по вашей ссылке. Спасибо."
                    bot.send_message(user[0], response)
                except Exception as e:
                    logger.error(e)
    if not db.get_user(message.from_user.id):
        db.insert_user(message.from_user.id)
        logger.info(f"{message.from_user.id} has registered")


@bot.message_handler(commands=['users'])
def _(message):
    if message.from_user.id in config.admins:
        db = SQLighter(DB)
        logger.info("getting list of alive users")
        response = '<b>Список пользователей:</b>'
        for user in db.get_users():
            try:
                bot.send_chat_action(user[0], 'typing')
            except:
                logger.info(f"user {user[0]} blocked bot")
                db.delete_user(user[0])
            else:
                response += f'\n<a href="tg://user?id={user[0]}">{user[0]}</a>'
        bot.send_message(message.chat.id, response, parse_mode='html')


@bot.message_handler(content_types=['document'])
def _(message):
    logger.info(f"{message.from_user.id} sent file")
    mes = None
    try:
        mes = bot.reply_to(message, "Обрабатываем...")
        user_id = message.from_user.id
        file_name = re.sub(r'[^a-zA-Z0-9\.\_]', '', message.document.file_name)
        if file_name == ".zip":
            file_name = "untitled.zip"
        bot_name, _ = os.path.splitext(file_name)
        if not re.search(r'[a-zA-Z0-9]', bot_name):
            bot_name = "untitled"
        downloaded_file = bot.download_file(
            bot.get_file(message.document.file_id).file_path)
        if message.document.mime_type != "application/zip":
            bot.edit_message_text("Файл должен быть формата zip!", mes.chat.id,
                                  mes.message_id)
            logger.error(f"{message.from_user.id} sent wrong file (ext)")
            return
        path = f'./download/{user_id}/'
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
            logger.error(
                f"{message.from_user.id} sent wrong file (no requirements.txt or/and tostart.txt)"
            )
            return
        db = SQLighter(DB)
        bots = db.get_bots(user_id)
        exist = False
        for item in bots:
            if bot_name in item:
                db.update_bot(item[0], status=False)
                bot_id = item[0]
                exist = True
        if not exist:
            bot_id = backend.get_hash(user_id) + backend.get_hash(
                int(time.time() - EPOCH))
            db.insert_bot(bot_id, bot_name, False, 0, user_id)
        backend.deploy(bot_id, user_id, file_name)
        bot.edit_message_text("Файл принят!", mes.chat.id, mes.message_id)
        logger.info(
            f"Successfully set bot up: user_id {message.from_user.id}, bot_id {bot_id}"
        )
    except Exception as e:
        if mes:
            bot.edit_message_text("Произошла ошибка... Попробуйте еще раз.",
                                  mes.chat.id, mes.message_id)
        else:
            bot.reply_to(message, "Произошла ошибка... Попробуйте еще раз.")
        if not db.get_user(message.from_user.id):
            db.insert_user(message.from_user.id)
        logger.error(e)


@bot.message_handler(regexp='^/bot_(\w+) (\w+)$')
def _(message):
    if re.search('^/bot_(\w+) (\w+)$', message.text):
        reg = re.search('^/bot_(\w+) (\w+)$', message.text)
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
                logger.info(
                    f"{message.from_user.id} sent command '{command}' to bot {bot_id}"
                )
                result = backend.controlbot(bot_id, command)
                if result[0] == 0:
                    bot.reply_to(message, result[1])
                elif result[0] == 10:
                    bot.send_document(message.from_user.id, result[1])
                    result[1].close()
                else:
                    bot.reply_to(
                        message,
                        f'Произошла ошибка. Код ошибки: {result[0]}\n{result[1]}'
                    )
            else:
                response = "<i>Нет такого бота...</i>"
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                     row_width=3)
                keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
                keyboard.row("📬 Помощь", "💻 О проекте")
                bot.send_message(message.chat.id,
                                 response,
                                 reply_markup=keyboard,
                                 parse_mode='html')
        else:
            response = "<i>Forbidden</i>"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True,
                                                 row_width=3)
            keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
            keyboard.row("📬 Помощь", "💻 О проекте")
            bot.send_message(message.chat.id,
                             response,
                             reply_markup=keyboard,
                             parse_mode='html')


@bot.message_handler(commands=['feedback'])
def _(message):
    if re.search('/feedback (.*)', message.text):
        report = re.search('/feedback (.*)', message.text, re.DOTALL).group(1)
        uid = message.from_user.id
        mesid = message.message_id
        user_info = f'{message.from_user.first_name}'
        try:
            user_info += f' (@{message.from_user.username})'
        except:
            pass
        response = f"[{uid} {mesid}]\nПользователь {user_info} оставил сообщение:\n{report}"
        bot.send_message(FEEDBACK, response)
        bot.send_message(message.from_user.id,
                         'Спасибо, с Вами скоро свяжутся')
    else:
        response = \
"<code>/feedback {сообщение}</code>\
\n\nПоддерживаются только текстовые сообщения."

        bot.send_message(message.from_user.id, response, parse_mode='html')


@bot.channel_post_handler()
def _(message):
    try:
        feedback = message.reply_to_message.text
    except:
        feedback = None
    if feedback:
        uid = re.search(r'\[(\d+) (\d+)\]', feedback).group(1)
        mesid = re.search(r'\[(\d+) (\d+)\]', feedback).group(2)
        response = f"Ответ поддержки:\n{message.text}"
        bot.send_message(uid, response, reply_to_message_id=mesid)


@bot.message_handler(content_types=["text"])
def _(message):
    if message.text == "⬇️ Загрузить бота":
        response = \
"Для обновления файлов бота загрузите файл в формате <i>bot_name.zip</i>, \
где <i>bot_name</i> - имя обновляемого бота. Для загрузки нового бота имя <i>bot_name</i> должно быть уникальным. \
\n\nВ архиве также должны содержаться следующие файлы: \
- <code>requerements.txt</code>, в котором указаны зависимости вашего проекта \
- <code>tostart.txt</code>, в котором указано, какой файл нам нужно запускать \
<b>\n\nВажно! У нас установлен интерпретатор Python 3.6.8, \
Позаботьтесь о совместимости Вашего кода!</b> \
\n\nЧто-то непонятно? Смотри <a href='https://telegra.ph/DeployMEbot-Gajd-07-08'>гайд.</a>"

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("📬 Помощь", "💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html',
                         disable_web_page_preview=True)
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
            response += f"""
<b>{item[1]}</b> [<i>{status}</i>]
ID бота: <code>{item[0]}</code>
Осталось времени: <i>{item[3]}</i>\n"""
        if not response:
            response = "\n<i>Пусто...</i>"
        response = "Ваши боты:\n" + response
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "📬 Помощь")
        keyboard.row("💻 О проекте")
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
        keyboard.row("💥 Удалить бота", "📬 Помощь")
        keyboard.row("💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "🧩 Обновить файлы":
        response = \
"Для обновления файлов бота загрузите файл в формате <i>bot_name.zip</i>, \
где <i>bot_name</i> - имя обновляемого бота. Для загрузки нового бота имя <i>bot_name</i> должно быть уникальным. \
\n\nВ архиве также должны содержаться следующие файлы: \
- <code>requerements.txt</code>, в котором указаны зависимости вашего проекта \
- <code>tostart.txt</code>, в котором указано, какой файл нам нужно запускать \
<b>\n\nВажно! У нас установлен интерпретатор Python 3.6.8, \
Позаботьтесь о совместимости Вашего кода!</b> \
\n\nНепонятно? Смотри <a href='https://telegra.ph/DeployMEbot-Gajd-07-08'>гайд.</a>"

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "📬 Помощь")
        keyboard.row("💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html',
                         disable_web_page_preview=True)
    elif message.text == "💥 Удалить бота":
        response = """Удалить бота:

/bot_remove {id}

<b>Внимание! После отправки команды бот окончательно будет удален.</b>"""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "📬 Помощь")
        keyboard.row("💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "💬 Посмотреть логи":
        response = "Посмотреть логи:\n\n/bot_logs {id}"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "🧩 Обновить файлы")
        keyboard.row("🚀 Запуск/остановка", "💬 Посмотреть логи")
        keyboard.row("💥 Удалить бота", "📬 Помощь")
        keyboard.row("💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "📬 Помощь":
        response = \
"Гайд по установке бота: https://telegra.ph/DeployMEbot-Gajd-07-08\
\nДля связи: <code>/feedback {сообщение}</code>"

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("📬 Помощь", "💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    elif message.text == "💻 О проекте":
        response = \
"Этот бот позволяет развернуть Вашего бота \
на сервере, чтобы держать его запущенным 24/7. \
\nДля связи: <code>/feedback {сообщение}</code>"

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("📬 Помощь", "💻 О проекте")
        bot.send_message(message.chat.id,
                         response,
                         reply_markup=keyboard,
                         parse_mode='html')
    else:
        response = 'Выберите интересующий Вас элемент меню:'
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
        keyboard.row("🔐 Панель управления", "⬇️ Загрузить бота")
        keyboard.row("📬 Помощь", "💻 О проекте")
        bot.send_message(message.chat.id, response, reply_markup=keyboard)


if __name__ == '__main__':
    try:
        bot.remove_webhook()
    except:
        pass
    if MODE == 1:
        bot.set_webhook(f"https://telegram.itsgay.club/{config.token}")
        cherrypy.config.update({
            'server.socket_host': '127.0.0.1',
            'server.socket_port': 7773,
            'engine.autoreload.on': True
        })
        cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
    elif MODE == 0:
        # Если нужно прокси (вписать свои) в файл proxy.py
        if PROXYLIST:
            apihelper.proxy = PROXYLIST
        bot.polling(none_stop=True)
