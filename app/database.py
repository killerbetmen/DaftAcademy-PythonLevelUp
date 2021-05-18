import os
import psycopg2

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
DATABASE_URL = os.environ["DATABASE_URL"]

engine = psycopg2.connect(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
