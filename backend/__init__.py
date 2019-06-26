# python wrapping for prepearing file system script
import subprocess  # safelly run bash scripts from python
import sys  # redirect stdout
from dmbhelper import SQLighter
import os
import config

DB = config.db
PATH = os.getcwd()


def deploy(user_id, arch):
    # run bash script and redirect stdout
    file = "{}/backend/preparefiles.sh".format(PATH)
    sub = subprocess.run([file, str(user_id), arch, PATH], stdout=sys.stdout)
    if not sub.returncode:
        print("ok")
        return (0)
    else:
        return (sub.stderr)
        return (1)


def controlbot(bot_id, command):
    """Принимает аргументы:
    bot_id - ID бота
    path - путь в папку с ботом (как и в deploy)
    command - одна из 4 команд (есть в config.py)
    start, stop, restart - аргументы для bot.sh
    logs - для вывода содержимого 'log/main.log'
    remove - запускать процесс удаления (backend/removefiles.sh)
    эта функция должна возвращать текст - результат работы
    примеры: return 'Бот запущен!'
    return mainlog"""
    db = SQLighter(DB)
    bot = db.get_bot(bot_id)
    path = "{}/bots/{}/{}".format(PATH, bot[4], bot[1])
    if command in ['start', 'stop']:
        file = "{}/bot.sh".format(path)
        sub = subprocess.run([file, command, path], stdout=sys.stdout)
        stat = subprocess.run([file, 'status', path], stdout=sys.stdout)
        if stat.returncode == 4:
            db.update_bot(bot_id, status=1)
        elif stat.returncode == 5:
            db.update_bot(bot_id, status=0)
        if not sub.returncode:
            print("ok")
            return (0)
        else:
            return (sub.stderr)
            return (1)
    elif command == 'remove':
        file = "{}/backend/removefiles.sh".format(PATH)
        sub = subprocess.run([file, str(bot_id), PATH], stdout=sys.stdout)
        if not sub.returncode:
            print("ok")
            return (0)
        else:
            return (sub.stderr)
            return (1)
    elif command == 'logs':
        file_path = "{}/log/bot.log".format(path)
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    logs = file.read()
                if logs:
                    return logs
        return "Пусто..."
    return None


def check_status(bot_id):
    db = SQLighter(DB)
    bot = db.get_bot(bot_id)
    path = "{}/bots/{}/{}".format(PATH, bot[4], bot[1])
    file = "{}/bot.sh".format(path)
    stat = subprocess.run([file, 'status', path], stdout=sys.stdout)
    if stat.returncode == 4:
        db.update_bot(bot_id, status=1)
    elif stat.returncode == 5:
        db.update_bot(bot_id, status=0)
    return 5 - stat.returncode


def get_hash(num):
    from_base = 10
    to_base = 36
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alphabet[n]
    else:
        return get_hash(n // to_base) + alphabet[n % to_base]


def main():
    pass


if __name__ == '__main__':
    main()
