from fastapi import FastAPI

from database import get_hospitals

app = FastAPI()


@app.get("/")
def home():
    return {"message": "Hospital API is running"}


@app.get("/hospitals")
def hospitals():
    return get_hospitals()
