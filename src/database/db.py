from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base,PatientEncounter
from config import DB_STRING

# Create a SQLAlchemy engine using the database URL from config.py
engine = create_engine(DB_STRING, echo=True)  # Set echo=True for SQL query logging


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base.metadata.create_all(engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


