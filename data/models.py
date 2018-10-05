import sqlite3

def insert_user(username, password):
	con = sqlite3.connect('data/users.db')
	cur = con.cursor()
	cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
	con.commit()
	con.close()

def retrieve_users():
	con = sqlite3.connect('users.db')
	cur = con.cursor()
	cur.execute("SELECT username, password FROM users")
	users = cur.fetchall()
	con.close()
	return users