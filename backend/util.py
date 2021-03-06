# python wrapping for prepearing file system script
from time import sleep
import subprocess  # safelly run bash scripts from python
import sys  # redirect stdout
import os
import logging
from backend import config
from backend.dmbhelper import SQLighter

DB = config.db
PATH = os.getcwd()


def deploy(bot_id, user_id, arch):
    # run bash script and redirect stdout
    logger.info(f'Processing deploy of {user_id} {bot_id}')
    file = f"{PATH}/backend/preparefiles.sh"
    sub = subprocess.run([file, str(user_id), bot_id, arch, PATH],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    if not sub.returncode:
        logger.info(f'Successfully deployed {bot_id} {user_id} from {arch}')
        return 0
    else:
        msg = ''
        if sub.stdout:
            msg += sub.stdout.decode('utf-8')
        if sub.stderr:
            msg += '\n' + sub.stderr.decode('utf-8')
        logger.error(msg)
        return sub.returncode


def controlbot(bot_id, command):
    # control user bots
    db = SQLighter(DB)
    bot = db.get_bot(bot_id)
    path = f"{PATH}/bots/{bot[4]}/{bot[1]}"
    if command in ['start', 'stop']:
        file = f"{path}/bot.sh"
        sub = subprocess.Popen([file, command, path])
        sleep(2)
        stat = subprocess.run([file, 'status', path], stdout=sys.stdout)
        logger.info(f'{stat.returncode}')
        if stat.returncode == 4:
            db.update_bot(bot_id, status=1)
        elif stat.returncode == 5:
            db.update_bot(bot_id, status=0)
        return 0, 'Слушаюсь!'
    elif command == 'remove':
        file = f"{PATH}/backend/removefiles.sh"
        sub = subprocess.run([file, str(bot_id), PATH],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        if not sub.returncode:
            logger.info(f'Successfully removed bot {bot_id}')
            return 0, 'Успешно!'
        else:
            msg = ''
            if sub.stdout:
                logger.info(f"{bot_id}: {sub.stdout.decode('utf-8')}")
                msg += sub.stdout.decode('utf-8')
            if sub.stderr:
                logger.error(f"{bot_id}: {sub.stderr.decode('utf-8')}")
                msg += '\n' + sub.stderr.decode('utf-8')
            return sub.returncode, msg
    elif command == 'logs':
        logger.info(f'send logs of {bot_id}')
        file_path = f"{path}/log/bot.log"
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                return 10, open(file_path, 'r')
        return 0, "Не найдено..."
    return 100, None


def check_status(bot_id):
    # checks status of user bot
    logger.info(f'Checking status of {bot_id}')
    db = SQLighter(DB)
    bot = db.get_bot(bot_id)
    path = f"{PATH}/bots/{bot[4]}/{bot[1]}"
    file = f"{path}/bot.sh"
    stat = subprocess.run([file, 'status', path],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE)
    if stat.stdout:
        logger.info(f"{bot_id}: {stat.stdout.decode('utf-8')}")
    if stat.stderr:
        logger.error(f"{bot_id}: {stat.stderr.decode('utf-8')}")
    if stat.returncode == 4:
        db.update_bot(bot_id, status=1)
    elif stat.returncode == 5:
        db.update_bot(bot_id, status=0)
    return 5 - stat.returncode


def get_hash(num):
    # generating hash
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


def get_logger(name, file):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(file)
    logger.addHandler(fh)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    return logger


def main():
    pass


if __name__ == '__main__':
    main()
else:
    logger = get_logger('Util', f'{PATH}/log/deploymebot.log')
