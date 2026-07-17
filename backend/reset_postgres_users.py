import psycopg2

postgres_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

conn = psycopg2.connect(postgres_url)
cur = conn.cursor()

# Clear friendships first due to foreign key
cur.execute("DELETE FROM friendships")
# Clear users
cur.execute("DELETE FROM users")

conn.commit()
print("Postgres users and friendships cleared.")
conn.close()
