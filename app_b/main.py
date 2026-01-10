from fastapi import FastAPI
from typing import List, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Person
import os

app = FastAPI()


# Database connection from environment variables
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "mydb")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)

# Create table if not exists
Base.metadata.create_all(engine)

@app.post("/receive-data")
def receive_data(items: List[Dict]):
    db = SessionLocal()
    saved = []
    try:
        for item in items:
            person = Person(
                id=item["id"],
                name=item["name"],
                age=item["age"],
                email=item["email"]
            )
            db.merge(person)  # merge avoids duplicate primary key
            saved.append(item)
        db.commit()
    except Exception as e:
        db.rollback()
        return {"error": str(e)}
    finally:
        db.close()
    return {"status": "received", "row_count": len(saved), "data_saved": saved}

# make a simple API to see data
#If you don’t want pgAdmin, you can add a GET endpoint in Container B:
#Call GET http://localhost:8001/person . You’ll get all rows in JSON format in your browser
# This is a very easy way to check stored data without a DB client.
@app.get("/person")
def get_persons():
    db = SessionLocal()
    try:
        rows = db.query(Person).all()
        return [ {"id": p.id, "name": p.name, "age": p.age, "email": p.email} for p in rows ]
    finally:
        db.close()