# python wrapping for prepearing file system script
import subprocess  # safelly run bash scripts from python
import sys  # redirect stdout


def deploy(user_id, arch, path):
    # run bash script and redirect stdout
    sub = subprocess.run(["./backend/preparefiles.sh", str(user_id), arch, path],
                         stdout=sys.stdout)
    if not sub.returncode:
        print("ok")
        return(0)
    else:
        return(sub.stderr)
        return(1)


def controlbot(path, command):
    """Принимает аргументы:
    path - путь в папку с ботом (пример: ./bots/123/test/)
    command - одна из 4 команд (есть в config.py)
    start, stop, restart - аргументы для bot.sh
    logs - для вывода содержимого path+'log/main.log'
    remove - запускать процесс удаления (backend/removefiles.sh)
    эта функция должна возвращать текст - результат работы
    примеры: return 'Бот запущен!'
    return mainlog"""
    print(path, command)


def main():
    pass


if __name__ == '__main__':
    main()
