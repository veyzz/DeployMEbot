# -*- coding: utf-8 -*-
import sqlite3
import config
import json


BOTS_COUNT = config.bots_count


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id integer, balance real, bots text)")

    def select_all(self):
        with self.connection:
            return self.cursor.execute("SELECT * FROM users").fetchall()

    def select(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
            if result:
                return result[0]
            return None

    def insert(self, user_id):
        with self.connection:
            self.cursor.execute("INSERT INTO users VALUES (?, 0.0, '{}')", (user_id,))
            self.connection.commit()

    def update(self, user_id, field, value):
        with self.connection:
            sql = "UPDATE users SET {}=? WHERE id=?".format(field)
            self.cursor.execute(sql, (value, user_id))
            self.connection.commit()

    def __del__(self):
        self.connection.close()


def add_new_bot(user, bot_name):
    bots = json.loads(user[2])
    code = 0
    if bot_name not in bots.keys():
        if len(bots.keys()) < BOTS_COUNT:
            bots[bot_name] = {}
            bots[bot_name]['path'] = './bots/{}/{}'.format(user[0], bot_name)
            bots[bot_name]['status'] = False
            bots[bot_name]['expire_time'] = 0
            code = 1
        else:
            code = 2
    return json.dumps(bots), code
