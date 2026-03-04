from fastapi import FastAPI
import psycopg2
import os

app = FastAPI()

@app.get("/")
def home():
    return {"message": "TNEA Prediction System Running"}