import psycopg2

postgres_url = "postgresql://doadmin:AVNS_SNm-zDEGXzrviF6ZS31@trivia-database-v2-do-user-18505351-0.i.db.ondigitalocean.com:25060/defaultdb?sslmode=require"

try:
    conn = psycopg2.connect(postgres_url)
    cur = conn.cursor()
    cur.execute("SELECT id, username, email, xp, level, chips, gems, rating FROM users ORDER BY id ASC")
    users = cur.fetchall()
    
    print(f"Total users in V2 Postgres Database: {len(users)}")
    print("-" * 80)
    print(f"{'ID':<5} | {'Username':<15} | {'Email':<30} | {'XP':<6} | {'Level':<5} | {'Chips':<6} | {'Gems':<5} | {'Rating':<5}")
    print("-" * 80)
    
    for u in users:
        print(f"{u[0]:<5} | {u[1]:<15} | {u[2]:<30} | {u[3]:<6} | {u[4]:<5} | {u[5]:<6} | {u[6]:<5} | {u[7]:<5}")
        
    conn.close()
except Exception as e:
    print("Database connection or query error:", e)
