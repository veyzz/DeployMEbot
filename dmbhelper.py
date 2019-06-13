# -*- coding: utf-8 -*-
import sqlite3


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
            return self.cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchall()

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
