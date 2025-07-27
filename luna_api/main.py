# File: luna_api/main.py

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select

# Local application imports
import auth
import models
from database import engine, get_session # Make sure you have database.py

# Pydantic models for data validation
class GuardianCreate(models.SQLModel):
    email: str
    password: str

# FastAPI App Initialization
app = FastAPI(title="L.U.N.A.")

@app.on_event("startup")
def on_startup():
    models.SQLModel.metadata.create_all(engine)

# API Endpoints
@app.post("/signup", response_model=models.Guardian)
def create_guardian(guardian_data: GuardianCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(models.Guardian).where(models.Guardian.email == guardian_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(guardian_data.password)
    db_guardian = models.Guardian(email=guardian_data.email, hashed_password=hashed_password)
    
    session.add(db_guardian)
    session.commit()
    session.refresh(db_guardian)
    return db_guardian

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    guardian = session.exec(select(models.Guardian).where(models.Guardian.email == form_data.username)).first()
    if not guardian or not auth.verify_password(form_data.password, guardian.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = auth.create_access_token(data={"sub": guardian.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=models.Guardian)
def read_users_me(current_guardian: models.Guardian = Depends(auth.get_current_guardian)):
    # This is a test endpoint to check if authentication is working.
    # It uses our dependency to get the current user and returns their data.
    return current_guardian