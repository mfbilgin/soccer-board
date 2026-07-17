import psycopg2
import os

postgres_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

conn = psycopg2.connect(postgres_url)
cur = conn.cursor()

cur.execute("SELECT id, username, email FROM users")
users = cur.fetchall()

print("Users in Postgres:")
for u in users:
    print(u)

conn.close()
