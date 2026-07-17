import psycopg2
import sqlite3

postgres_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
sqlite_path = "C:/Users/PC/Desktop/project/football_trivia.db"

pg_conn = psycopg2.connect(postgres_url)
pg_cur = pg_conn.cursor()
pg_cur.execute("SELECT id, username, hashed_password FROM users")
print("Postgres users:", pg_cur.fetchall())

try:
    sq_conn = sqlite3.connect(sqlite_path)
    sq_cur = sq_conn.cursor()
    sq_cur.execute("SELECT id, username, hashed_password FROM users")
    print("SQLite users:", sq_cur.fetchall())
except Exception as e:
    print("Local sqlite error:", e)
