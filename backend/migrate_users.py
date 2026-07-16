import sqlite3
import psycopg2
import os

sqlite_db_path = os.path.join(os.path.dirname(__file__), "football_trivia.db")
if not os.path.exists(sqlite_db_path):
    sqlite_db_path = os.path.join(os.path.dirname(__file__), "..", "football_trivia.db")

postgres_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

print(f"Connecting to SQLite: {sqlite_db_path}")
sqlite_conn = sqlite3.connect(sqlite_db_path)
sqlite_cur = sqlite_conn.cursor()

pg_conn = psycopg2.connect(postgres_url)
pg_cur = pg_conn.cursor()

def table_exists(cur, table_name):
    cur.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = %s)", (table_name,))
    return cur.fetchone()[0]

if not table_exists(pg_cur, "users"):
    print("Postgres users table doesn't exist yet! Run backend once to create it.")
    exit(1)

# Migrate Users
sqlite_cur.execute("SELECT id, username, email, hashed_password, xp, level, chips, gems, rating FROM users")
users = sqlite_cur.fetchall()

pg_cur.execute("SELECT id FROM users")
existing_user_ids = {row[0] for row in pg_cur.fetchall()}

users_to_insert = [u for u in users if u[0] not in existing_user_ids]
if users_to_insert:
    pg_cur.executemany(
        "INSERT INTO users (id, username, email, hashed_password, xp, level, chips, gems, rating) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
        users_to_insert
    )
    print(f"Migrated {len(users_to_insert)} users.")
else:
    print("No new users to migrate.")

# Migrate Friendships
if table_exists(pg_cur, "friendships"):
    sqlite_cur.execute("SELECT id, user_id, friend_id, status FROM friendships")
    friendships = sqlite_cur.fetchall()
    
    pg_cur.execute("SELECT id FROM friendships")
    existing_friendship_ids = {row[0] for row in pg_cur.fetchall()}
    
    friendships_to_insert = [f for f in friendships if f[0] not in existing_friendship_ids]
    if friendships_to_insert:
        pg_cur.executemany(
            "INSERT INTO friendships (id, user_id, friend_id, status) VALUES (%s, %s, %s, %s)",
            friendships_to_insert
        )
        print(f"Migrated {len(friendships_to_insert)} friendships.")
    else:
        print("No new friendships to migrate.")

pg_conn.commit()
pg_conn.close()
sqlite_conn.close()
print("Migration completed successfully.")
