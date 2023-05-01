import datetime
import os
import sqlite3

from bot import PYTHONANYWHERE_LOGIN

conn = sqlite3.connect(os.path.join(f"/home/{PYTHONANYWHERE_LOGIN}/bot/db", "statistic.db"))
cursor = conn.cursor()

date = datetime.datetime.today().date()


def tracking(manager_name):
    global date
    if date == datetime.datetime.today().date():
        cursor.execute(
            f"UPDATE statistics SET users = users + 1 WHERE manager_name = '{manager_name}' AND date = '{datetime.datetime.today().date()}'")
        conn.commit()
    else:
        check_db_exists()
        cursor.execute(f"UPDATE statistics SET users = users + 1 WHERE manager_name = '{manager_name}' AND date = '{datetime.datetime.today().date()}'")
        conn.commit()
        date = datetime.datetime.today().date()


def get_today_statistic():
    statistic = cursor.execute(
        f"SELECT manager_name, users FROM statistics WHERE date = '{datetime.datetime.today().date()}'"
    ).fetchall()
    return statistic


def get_yesterday_statistic():
    statistic = cursor.execute(
        f"SELECT manager_name, users FROM statistics WHERE date = '{datetime.datetime.today().date() - datetime.timedelta(days=1)}'"
    ).fetchall()
    return statistic


def get_statistic(date):
    statistic = cursor.execute(
        f"SELECT manager_name, users FROM statistics WHERE date = '{date}'"
    ).fetchall()
    return statistic


def get_large_statistic(date1, date2):
    statistic = cursor.execute(
        f"SELECT manager_name, users FROM statistics WHERE date BETWEEN '{date1}' AND '{date2}'"
    ).fetchall()
    return statistic


def _init_db():
    """Инициализирует БД"""
    with open(f"/home/{PYTHONANYWHERE_LOGIN}/bot/createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='statistics'")
    table_exists = cursor.fetchall()
    if not table_exists:
        _init_db()
    with open(f'/home/{PYTHONANYWHERE_LOGIN}/bot/managers.txt') as file:
        lines = file.readlines()
        for line in lines:
            if '\n' in line:
                line = line.replace('\n', '')
            check = cursor.execute(f"SELECT manager_name FROM statistics WHERE manager_name='{line}' AND date='{datetime.datetime.today().date()}'").fetchone()
            if check is None:
                cursor.execute(f"INSERT INTO statistics (manager_name, date, users) VALUES ('{line}', '{datetime.datetime.today().date()}', 0)")
                conn.commit()


check_db_exists()