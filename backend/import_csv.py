import os
import pandas as pd
from database import SessionLocal, engine
import models

print("Dropping old tables and creating new schema...")
models.Base.metadata.drop_all(bind=engine)
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

def import_table(csv_name, model_class):
    print(f"Importing {csv_name}...")
    file_path = os.path.join("..", "database_backup", csv_name)
    df = pd.read_csv(file_path, low_memory=False)
    
    # NaN değerleri None ile değiştir (SQLAlchemy NULL)
    df = df.where(pd.notnull(df), None)
    
    records = df.to_dict(orient="records")
    
    # SQLite'ta çok büyük listeleri tek seferde basmak sorun olabilir, batch'lere bölelim
    batch_size = 10000
    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        db.bulk_insert_mappings(model_class, batch)
    db.commit()
    print(f"Completed {csv_name} ({len(records)} rows)")

import_table("players.csv", models.Player)
import_table("teams.csv", models.Team)
import_table("competitions.csv", models.Competition)
import_table("player_club_stats.csv", models.PlayerClubStat)
import_table("player_national_stats.csv", models.PlayerNationalStat)
import_table("player_transfers.csv", models.PlayerTransfer)
print("Database built successfully!")
db.close()
