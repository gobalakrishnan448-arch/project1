from fastapi import FastAPI
import psycopg2
import os
from sqlalchemy import create_engine, text

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL,connect_args={"sslmode":"require"})

@app.get("/setup-db")
def setup_db():
    with engine.connect() as connection:

        # Colleges Table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS colleges (
                id SERIAL PRIMARY KEY,
                college_name TEXT NOT NULL,
                district TEXT,
                college_type TEXT
            );
        """))

        # Branches Table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS branches (
                id SERIAL PRIMARY KEY,
                branch_name TEXT NOT NULL
            );
        """))

        # Cutoffs Table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS cutoffs (
                id SERIAL PRIMARY KEY,
                college_id INT REFERENCES colleges(id) ON DELETE CASCADE,
                branch_id INT REFERENCES branches(id) ON DELETE CASCADE,
                year INT,
                round INT,
                community TEXT,
                quota TEXT,
                cutoff FLOAT
            );
        """))

        connection.commit()

    return {"message": "Professional Tables Created Successfully"}