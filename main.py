from fastapi import FastAPI
import psycopg2
import os
from sqlalchemy import create_engine, text

app = FastAPI()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL,connect_args={"sslmode":"require"})

@app.get("/predict")
def predict(cutoff: float, community: str):

    query = text(f"""
    SELECT college_name, branch_name, district, cutoff_{community}
    FROM cutoff_data
    WHERE cutoff_{community} IS NOT NULL
    """)

    with engine.connect() as connection:
        result = connection.execute(query)
        rows = result.fetchall()

    colleges = []

    for row in rows:
        diff = cutoff - row[3]

        if diff >= 3:
            round_name = "Round 1 (Safe)"
        elif diff >= 1:
            round_name = "Round 2 (Moderate)"
        elif diff >= -1:
            round_name = "Round 3 (Risky)"
        else:
            continue

        colleges.append({
            "college": row[0],
            "branch": row[1],
            "district": row[2],
            "last_cutoff": row[3],
            "chance": round_name
        })

    colleges = sorted(colleges, key=lambda x: x["last_cutoff"], reverse=True)

    return colleges[:20]

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

@app.get("/insert-sample-data")
def insert_data():
    with engine.connect() as connection:
        connection.execute(text("""
        INSERT INTO colleges (college_name, branch, district, cutoff, community)
        VALUES 
        ('PSG College of Technology','CSE','Coimbatore',198,'OC'),
        ('SSN College of Engineering','CSE','Chennai',197,'OC'),
        ('Thiagarajar College of Engineering','IT','Madurai',195,'BC'),
        ('Kongu Engineering College','CSE','Erode',194,'BC'),
        ('Coimbatore Institute of Technology','CSE','Coimbatore',196,'OC')
        """))

        connection.commit()

    return {"message": "Sample Data Inserted"}