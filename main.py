from typing import Annotated

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from database import (
    get_hospitals,
    get_emergency_hospitals,
    get_hospital_readmissions
)

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"])


@app.get("/")
def home():
    return {"message": "Hospital API is running"}


@app.get("/hospitals")
def hospitals(
    state: Annotated[str | None, Query(pattern="^[A-Za-z]{2}$")] = None,
    rating: Annotated[int | None, Query(ge=1, le=5)] = None,
):
    return get_hospitals(state=state.upper() if state else None, rating=rating)


@app.get("/hospitals/emergency")
def emergency_hospitals(
    state: Annotated[str, Query(pattern="^[A-Za-z]{2}$")] = "CA"
):
    return get_emergency_hospitals(state)


@app.get("/hospitals/readmissions")
def hospital_readmissions(
    state: Annotated[str,Query(pattern="^[A-Za-z]{2}$")] = "CA"
):
    return get_hospital_readmissions(state)
