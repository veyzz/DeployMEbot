# python wrapping for prepearing file system script
import subprocess  # safelly run bash scripts from python
import sys  # redirect stdout
from dmbhelper import SQLighter


def deploy(user_id, arch, path):
    # run bash script and redirect stdout
    sub = subprocess.run(
        ["./backend/preparefiles.sh",
         str(user_id), arch, path],
        stdout=sys.stdout)
    if not sub.returncode:
        print("ok")
        return (0)
    else:
        return (sub.stderr)
        return (1)


def controlbot(bot_id, command, path):
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
    print(bot_id, command, path)
    if command in ['start', 'stop', 'restart']:
        pass
    elif command == 'remove':
        sub = subprocess.run(
            ["./backend/removefiles.sh",
             str(bot_id), path],
            stdout=sys.stdout)
        if not sub.returncode:
            print("ok")
            return (0)
        else:
            return (sub.stderr)
            return (1)
    elif command == 'logs':
        pass


def main():
    pass


if __name__ == '__main__':
    main()
