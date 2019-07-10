# -*- coding: utf-8 -*-
import sqlite3
import time
from backend import util


class SQLighter:
    def __init__(self, database):
        self.connection = sqlite3.connect(database)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys=on")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS bots (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, status INTEGER, expire INTEGER,
            owner INTEGER NOT NULL, FOREIGN KEY (owner) REFERENCES users(id))"""
                            )
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY, balance REAL, ref_link TEXT, ref_count INTEGER,
            invited_by INTEGER, requirement REAL, reg_date INTEGER)""")

    def select_all(self, table):
        with self.connection:
            return self.cursor.execute(f"SELECT * FROM {table}").fetchall()

    def get_users(self):
        with self.connection:
            return self.cursor.execute(f"SELECT * FROM users").fetchall()

    def get_user(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE id = ?",
                                         (user_id, )).fetchall()
            if result:
                return result[0]
            return None

    def get_ref(self, ref):
        with self.connection:
            result = self.cursor.execute(
                "SELECT * FROM users WHERE ref_link = ?", (ref, )).fetchall()
            if result:
                return result[0]
            return None

    def get_bots(self, user_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM bots WHERE owner = ?",
                                       (user_id, )).fetchall()

    def get_bot(self, bot_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM bots WHERE id = ?",
                                         (bot_id, )).fetchall()
            if result:
                return result[0]
            return None

    def insert_user(self, user_id, by_id=None):
        with self.connection:
            ref = util.get_hash(user_id)
            reg_date = int(time.time())
            try:
                self.cursor.execute(
                    "INSERT INTO users VALUES (?, 0, ?, 0, ?, 10, ?)",
                    (user_id, ref, by_id, reg_date))
            except:
                print('failed to execute insert_user()')
            self.connection.commit()

    def insert_bot(self, *bot):
        with self.connection:
            try:
                self.cursor.execute("INSERT INTO bots VALUES (?, ?, ?, ?, ?)",
                                    bot)
            except:
                print('failed to execute insert_bot()')
            self.connection.commit()

    def update_user(self, user_id, **values):
        with self.connection:
            for field in values.keys():
                try:
                    self.cursor.execute(
                        f"UPDATE users SET {field}=? WHERE id=?",
                        (values[field], user_id))
                except:
                    print('failed to execute update_user()')
            self.connection.commit()

    def update_bot(self, bot_id, **values):
        with self.connection:
            for field in values.keys():
                try:
                    self.cursor.execute(
                        f"UPDATE bots SET {field}=? WHERE id=?",
                        (values[field], bot_id))
                except:
                    print('failed to execute update_bot()')
            self.connection.commit()

    def delete_user(self, user_id):
        with self.connection:
            try:
                self.cursor.execute("DELETE FROM users WHERE id = ?",
                                    (user_id, ))
            except:
                print('failed to execute delete_user()')
            self.connection.commit()

    def delete_bot(self, bot_id):
        with self.connection:
            try:
                self.cursor.execute("DELETE FROM bots WHERE id = ?",
                                    (bot_id, ))
            except:
                print('failed to execute delete_bot()')
            self.connection.commit()

    def __del__(self):
        self.connection.close()
