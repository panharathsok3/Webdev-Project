
from fastapi import FastAPI, HTTPException
from sqlalchemy import text
from database import engine, get_hospitals

app = FastAPI()


@app.get("/")
def home():
  return {"message": "Hospital API is running"}


@app.get("/hospitals")
def hospitals():
  return get_hospitals()