# -*- coding: utf-8 -*-
import os
from backend import config
from backend import SQLighter

PATH = os.getcwd()
DB = config.db


def main():
    db = SQLighter(DB)
    bots = db.get_running_bots()
    with open('toStart', 'w') as file:
        for item in bots:
            path = f'{PATH}/bots/{item[4]}/{item[1]}\n'
            file.write(path)


if __name__ == '__main__':
    main()
