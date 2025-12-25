import pyodbc
import os
from dotenv import load_dotenv
from flask import g

load_dotenv()

def get_db():
    if 'db' not in g:
        g.db = pyodbc.connect(
            f"DRIVER={{{os.getenv('DB_DRIVER')}}};"
            f"SERVER={os.getenv('DB_SERVER')};"
            f"DATABASE={os.getenv('DB_NAME')};"
            f"UID={os.getenv('DB_USER')};"
            f"PWD={os.getenv('DB_PASSWORD')};"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
    return g.db

def get_cursor():
    conn = get_db()
    return conn, conn.cursor()

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
