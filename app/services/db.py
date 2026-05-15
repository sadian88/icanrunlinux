import psycopg2
import psycopg2.extras

from app.config import DATABASE_URL


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def dict_row(cursor, row):
    return {desc[0]: val for desc, val in zip(cursor.description, row)}
