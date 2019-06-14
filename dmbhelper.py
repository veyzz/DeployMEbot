# -*- coding: utf-8 -*-
import sqlite3


class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys=on")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY, name TEXT NOT NULL, status INTEGER, expire INTEGER,
            owner INTEGER NOT NULL, FOREIGN KEY (owner) REFERENCES users(id))""")
        self.cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, balance REAL)")

    def select_all(self, table):
        with self.connection:
            sql = "SELECT * FROM {}".format(table)
            return self.cursor.execute(sql).fetchall()

    def get_user(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()
            if result:
                return result[0]
            return None

    def get_bots(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM bots WHERE owner = ?", (user_id,)).fetchall()

    def insert_user(self, user_id):
        with self.connection:
            self.cursor.execute("INSERT INTO users VALUES (?, 0)", (user_id,))
            self.connection.commit()

    def insert_bot(self, *bot):
        with self.connection:
            self.cursor.execute("INSERT INTO bots VALUES (?, ?, ?, ?, ?)", bot)
            self.connection.commit()

    def update_user(self, user_id, **values):
        with self.connection:
            for field in values.keys():
                sql = "UPDATE users SET {}=? WHERE id=?".format(field)
                self.cursor.execute(sql, (values[field], user_id))
            self.connection.commit()

    def update_bot(self, bot_id, **values):
        with self.connection:
            for field in values.keys():
                sql = "UPDATE bots SET {}=? WHERE id=?".format(field)
                self.cursor.execute(sql, (values[field], bot_id))
            self.connection.commit()

    def __del__(self):
        self.connection.close()
