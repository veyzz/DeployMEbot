# python wrapping for prepearing file system script
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
    logger.info('Processing deploy')
    file = f"{PATH}/backend/preparefiles.sh"
    sub = subprocess.run([file, str(user_id), bot_id, arch, PATH],
                         stdout=sys.stdout)
    if not sub.returncode:
        logger.info(f'Successfully deployed {bot_id} {user_id} from {arch}')
        return (0)
    else:
        logger.error(sub.stderr)
        return (sub.stderr)
        return (1)


def controlbot(bot_id, command):
    # control user bots
    db = SQLighter(DB)
    bot = db.get_bot(bot_id)
    path = f"{PATH}/bots/{bot[4]}/{bot[1]}"
    if command in ['start', 'stop']:
        file = f"{path}/bot.sh"
        sub = subprocess.run([file, command, path],
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stat = subprocess.run([file, 'status', path], stdout=sys.stdout)
        if stat.returncode == 4:
            db.update_bot(bot_id, status=1)
        elif stat.returncode == 5:
            db.update_bot(bot_id, status=0)
        if not sub.returncode:
            logger.info(f'Successfully turned bot {bot_id}')
            return 0, 'Success'
        else:
            msg = ''
            if sub.stdout:
                logger.error(sub.stdout.decode('utf-8'))
                msg += sub.stdout.decode('utf-8')
            if sub.stderr:
                logger.error(sub.stderr.decode('utf-8'))
                msg += '\n' + sub.stderr.decode('utf-8')
            return sub.returncode, msg
    elif command == 'remove':
        file = f"{PATH}/backend/removefiles.sh"
        sub = subprocess.run([file, str(bot_id), PATH], stdout=sys.stdout)
        if not sub.returncode:
            logger.info(f'Successfully removed bot {bot_id}')
            return 0, 'Success'
        else:
            msg = ''
            if sub.stdout:
                logger.error(sub.stdout.decode('utf-8'))
                msg += sub.stdout.decode('utf-8')
            if sub.stderr:
                logger.error(sub.stderr.decode('utf-8'))
                msg += '\n' + sub.stderr.decode('utf-8')
            return sub.returncode, msg
    elif command == 'logs':
        logger.info(f'reading logs of {bot_id}')
        file_path = f"{path}/log/bot.log"
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                with open(file_path, 'r') as file:
                    logs = file.read()
                if logs:
                    return logs
        return "Пусто..."
    return None


def check_status(bot_id):
    # checks status of user bot
    logger.info(f'Checking status of {bot_id}')
    db = SQLighter(DB)
    bot = db.get_bot(bot_id)
    path = f"{PATH}/bots/{bot[4]}/{bot[1]}"
    file = f"{path}/bot.sh"
    stat = subprocess.run([file, 'status', path], stdout=sys.stdout)
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
