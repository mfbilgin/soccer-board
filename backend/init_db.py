from sqlalchemy import create_engine
from models import Base

# Using SQLite for development
DATABASE_URL = "sqlite:///football_trivia.db"

def init_db():
    print(f"Connecting to database at {DATABASE_URL}...")
    engine = create_engine(DATABASE_URL, echo=True)
    
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(engine)
    print("Database initialization complete.")

if __name__ == "__main__":
    init_db()
