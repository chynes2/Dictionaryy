import sqlite3

conn = sqlite3.connect('users.db')

c = conn.cursor()

statement = """CREATE TABLE users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	username TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL
);"""

c.execute(statement)

conn.commit()
conn.close()