from fastapi import FastAPI
import psycopg2
import os
from sqlalchemy import create_engine, text

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL,connect_args={"sslmode":"require"})

@app.get("/test-db")
def test_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"message": "Database Connected Successfully"}