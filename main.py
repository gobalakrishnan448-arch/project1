from fastapi import FastAPI
import os
from sqlalchemy import create_engine, text

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# Home
@app.get("/")
def home():
    return {"status": "API Running"}

# RESET DATABASE
@app.get("/reset-db")
def reset_db():

    with engine.begin() as conn:

        conn.execute(text("DROP TABLE IF EXISTS colleges"))

        conn.execute(text("""
        CREATE TABLE colleges (
            id SERIAL PRIMARY KEY,
            college_name TEXT,
            branch TEXT,
            district TEXT,
            cutoff FLOAT,
            community TEXT
        )
        """))

    return {"message": "Database Reset Done"}

# INSERT SAMPLE DATA
@app.get("/insert-sample-data")
def insert_data():

    with engine.begin() as conn:

        conn.execute(text("""
        INSERT INTO colleges (college_name, branch, district, cutoff, community)
        VALUES
        ('PSG College of Technology','CSE','Coimbatore',198,'OC'),
        ('SSN College of Engineering','CSE','Chennai',197,'OC'),
        ('Thiagarajar College of Engineering','IT','Madurai',195,'BC'),
        ('Kongu Engineering College','CSE','Erode',194,'BC'),
        ('Coimbatore Institute of Technology','CSE','Coimbatore',196,'OC')
        """))

    return {"message": "Sample Data Inserted"}

# PREDICT
@app.get("/predict")
def predict(cutoff: float, community: str):

    with engine.connect() as conn:

        result = conn.execute(text("""
        SELECT college_name, branch, district, cutoff
        FROM colleges
        WHERE cutoff <= :cutoff
        AND community = :community
        ORDER BY cutoff DESC
        LIMIT 20
        """), {"cutoff": cutoff, "community": community})

        rows = result.fetchall()

    data = []

    for r in rows:

        diff = cutoff - r[3]

        if diff >= 2:
            chance = "SAFE"
        elif diff >= 1:
            chance = "MODERATE"
        else:
            chance = "RISKY"

        data.append({
            "college": r[0],
            "branch": r[1],
            "district": r[2],
            "last_cutoff": r[3],
            "chance": chance
        })

    return data