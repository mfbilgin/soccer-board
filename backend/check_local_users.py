import sqlite3
import os

sqlite_path = "C:/Users/PC/Desktop/project/football_trivia.db"
conn = sqlite3.connect(sqlite_path)
cur = conn.cursor()
cur.execute("SELECT id, username, hashed_password FROM users")
print("Local SQLite users:", cur.fetchall())
