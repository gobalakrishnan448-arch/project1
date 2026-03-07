from fastapi import FastAPI
import os
from sqlalchemy import create_engine, text

app = FastAPI()

# ---------------------------
# DATABASE CONNECTION
# ---------------------------

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# ---------------------------
# PREDICT API
# ---------------------------

@app.get("/predict")
def predict(cutoff: float, community: str, district: str = "All"):

    query = """
    SELECT college_name, branch, district, cutoff, community
    FROM colleges
    WHERE cutoff <= :cutoff
    AND community = :community
    """

    if district != "All":
        query += " AND district = :district"

    query += " ORDER BY cutoff DESC LIMIT 20"

    with engine.connect() as conn:

        if district == "All":
            result = conn.execute(
                text(query),
                {"cutoff": cutoff, "community": community}
            )
        else:
            result = conn.execute(
                text(query),
                {
                    "cutoff": cutoff,
                    "community": community,
                    "district": district
                }
            )

        rows = result.fetchall()

    data = []

    for r in rows:

        difference = cutoff - r[3]

        if difference >= 2:
            chance = "SAFE"
        elif difference >= 1:
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


# ---------------------------
# CREATE TABLE
# ---------------------------
@app.get("/insert-sample-data")
def insert_data():

    with engine.begin() as connection:

        connection.execute(text("""
        INSERT INTO colleges (college_name, branch, district, cutoff, community)
        VALUES
        ('PSG College of Technology','CSE','Coimbatore',198,'OC'),
        ('SSN College of Engineering','CSE','Chennai',197,'OC'),
        ('Thiagarajar College of Engineering','IT','Madurai',195,'BC'),
        ('Kongu Engineering College','CSE','Erode',194,'BC'),
        ('Coimbatore Institute of Technology','CSE','Coimbatore',196,'OC')
        """))

    return {"message": "Sample Data Inserted"}