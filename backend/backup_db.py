import os
import csv
from sqlalchemy import create_engine, text

def backup_database():
    db_url = os.getenv("DATABASE_URL_V2")
    if not db_url:
        print("DATABASE_URL_V2 is not set!")
        return

    engine = create_engine(db_url)

    tables = [
        "players", 
        "teams", 
        "competitions", 
        "player_club_stats", 
        "player_national_stats", 
        "player_transfers"
    ]

    backup_dir = "C:\\Users\\PC\\Desktop\\project\\database_backup"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    with engine.connect() as conn:
        for table in tables:
            print(f"[{table}] Yedekleniyor...")
            # Use server side cursor by specifying stream_results=True if we were using core,
            # but with fetchmany it's usually fine for 1M rows on 64-bit python.
            # Using yield_per is better for ORM, but raw SQL fetchmany is okay.
            result = conn.execution_options(stream_results=True).execute(text(f"SELECT * FROM {table}"))
            columns = result.keys()
            
            file_path = os.path.join(backup_dir, f"{table}.csv")
            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                
                rows_written = 0
                while True:
                    chunk = result.fetchmany(50000)
                    if not chunk:
                        break
                    writer.writerows(chunk)
                    rows_written += len(chunk)
                    print(f"  -> {rows_written} satır yazıldı...")
            print(f"[{table}] Bitti. ({rows_written} satır)\n")

    print(f"Tüm veritabanı başarıyla yedeklendi: {backup_dir}")

if __name__ == "__main__":
    backup_database()
