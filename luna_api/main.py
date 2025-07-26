import os
from fastapi import FastAPI
from sqlmodel import create_engine, SQLModel
from luna_api.models import Guardian, Garment, Whisper

# This line connects to the database using the URL from our docker-compose file.
app = FastAPI(title="L.U.N.A. - Lifestyle Utility & Nurturing Assistant", description="L.U.N.A. Cares for You")

# This function tells our ORM to create the database tables based on our models.
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)


# We create the main FastAPI app instance.
# The on_startup event hook ensures our tables are created when the app starts.
@app.on_event("startup")
def on_startup():
    print("Creating database and tables...")
    SQLModel.metadata.create_all(engine)
    print("Database and tables created.")


# This is our first API endpoint. It listens for requests at the root URL ("/").
@app.get("/")
def read_root():
    return {"message": "Welcome to L.U.N.A. - LUNA Cares for You!"}