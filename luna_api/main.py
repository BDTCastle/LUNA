import os
from fastapi import FastAPI
from sqlmodel import create_engine, SQLModel
from models import Guardian, Garment, Whisper

app = FastAPI(title="L.U.N.A. - Lifestyle & Nurturing Assistant")

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

@app.get("/")
def read_root():
    return {"message": "Welcome to L.U.N.A.!"}