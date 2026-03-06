from fastapi import FastAPI
import os
from sqlalchemy import create_engine, text

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# ---------- Predict API ----------

@app.get("/predict")
def predict(cutoff: float):

    query = """
    SELECT college_name, branch, district, cutoff
    FROM colleges
    WHERE cutoff <= :cutoff
    ORDER BY cutoff DESC
    LIMIT 20
    """

    with engine.connect() as conn:
        result = conn.execute(text(query), {"cutoff": cutoff})
        rows = result.fetchall()

    data = []

    for r in rows:
        data.append({
            "college": r[0],
            "branch": r[1],
            "district": r[2],
            "last_cutoff": r[3]
        })

    return data


# ---------- Create Table ----------

@app.get("/setup-db")
def setup_db():

    with engine.connect() as connection:

        connection.execute(text("""

        CREATE TABLE IF NOT EXISTS colleges (

            id SERIAL PRIMARY KEY,
            college_name TEXT,
            branch TEXT,
            district TEXT,
            cutoff FLOAT,
            community TEXT

        )

        """))

        connection.commit()

    return {"message": "Table Created"}


# ---------- Insert Sample Data ----------

@app.get("/insert-sample-data")
def insert_data():

    with engine.connect() as connection:

        connection.execute(text("""

        INSERT INTO colleges
        (college_name, branch, district, cutoff, community)

        VALUES

        ('PSG College of Technology','CSE','Coimbatore',198,'OC'),
        ('SSN College of Engineering','CSE','Chennai',197,'OC'),
        ('Thiagarajar College of Engineering','IT','Madurai',195,'BC'),
        ('Kongu Engineering College','CSE','Erode',194,'BC'),
        ('Coimbatore Institute of Technology','CSE','Coimbatore',196,'OC')

        """))

        connection.commit()

    return {"message": "Sample Data Inserted"}