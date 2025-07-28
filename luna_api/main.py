# File: luna_api/main.py

# Reminder to self: This is the imports section.
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Optional, List
from apscheduler.schedulers.background import BackgroundScheduler

# Reminder to self: I'm importing all of our own project modules here.
import auth
import models
import services
from database import engine, get_session
import schemas

# Reminder to self: This is the function the scheduler will run in the background.
def generate_all_nudges():
    """This job finds all eligible users and creates a recommendation whisper for them."""
    print("Scheduler is running the daily nudge job...")
    with Session(engine) as session:
        guardians_to_nudge = session.exec(
            select(models.Guardian).where(models.Guardian.enable_nudges == True).where(models.Guardian.location != None)
        ).all()

        for guardian in guardians_to_nudge:
            try:
                # Assuming a default gender for automatic nudges for now
                recommendation = services.generate_weather_recommendation(city=guardian.location, gender="unisex")
                # The field in the Whisper model is 'message', not 'content'
                whisper = models.Whisper(message=recommendation, guardian_id=guardian.id)
                session.add(whisper)
            except Exception as e:
                print(f"Failed to generate nudge for guardian {guardian.id}: {e}")
        
        session.commit()
        print(f"Nudge job complete. Generated nudges for {len(guardians_to_nudge)} guardians.")

# Reminder to self: Create the scheduler instance.
scheduler = BackgroundScheduler()

# Reminder to self: This is the FastAPI app setup section.
app = FastAPI(title="L.U.N.A.")

# Reminder to self: This is the startup/shutdown event section.
@app.on_event("startup")
def on_startup():
    """This creates database tables and starts the background scheduler."""
    models.SQLModel.metadata.create_all(engine)
    scheduler.add_job(generate_all_nudges, 'interval', minutes=1)
    scheduler.start()

@app.on_event("shutdown")
def on_shutdown():
    """This cleanly shuts down the scheduler when the app stops."""
    scheduler.shutdown()

# Reminder to self: This is the API endpoints section.
@app.post("/signup", response_model=models.Guardian)
def create_guardian(guardian_data: schemas.GuardianCreate, session: Session = Depends(get_session)):
    """This endpoint creates a new user (Guardian)."""
    existing = session.exec(select(models.Guardian).where(models.Guardian.email == guardian_data.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(guardian_data.password)
    db_guardian = models.Guardian(
        email=guardian_data.email, 
        hashed_password=hashed_password,
        location=guardian_data.location,
        enable_nudges=True
    )
    session.add(db_guardian)
    session.commit()
    session.refresh(db_guardian)
    return db_guardian

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    guardian = session.exec(select(models.Guardian).where(models.Guardian.email == form_data.username)).first()
    if not guardian or not auth.verify_password(form_data.password, guardian.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # This line is critical: it must use str(guardian.id)
    token = auth.create_access_token(data={"sub": str(guardian.id)})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=models.Guardian)
def read_users_me(current_guardian: models.Guardian = Depends(auth.get_current_guardian)):
    """This is a test endpoint to check if authentication is working."""
    return current_guardian

@app.get("/recommendation")
def get_recommendation(gender: str, current_guardian: models.Guardian = Depends(auth.get_current_guardian)):
    """This is our core feature. It generates an outfit recommendation for the logged-in user."""
    if not current_guardian.location:
        raise HTTPException(
            status_code=400, 
            detail="No location found. Please set one via the /preferences endpoint."
        )
    
    recommendation = services.generate_weather_recommendation(city=current_guardian.location, gender=gender)
    return {"recommendation": recommendation}

@app.patch("/preferences", response_model=models.Guardian)
def update_preferences(
    preferences: schemas.PreferencesUpdate,
    current_guardian: models.Guardian = Depends(auth.get_current_guardian),
    session: Session = Depends(get_session)
):
    """This endpoint lets a logged-in user update their preferences."""
    # Handle simple, non-nested updates
    if preferences.location is not None:
        current_guardian.location = preferences.location
    if preferences.enable_nudges is not None:
        current_guardian.enable_nudges = preferences.enable_nudges
        
    # CRITICAL FIX: Specifically handle the complex 'habits' dictionary
    if preferences.habits is not None:
        current_habits = current_guardian.habits or {}
        new_habits = {key: value.model_dump() for key, value in preferences.habits.items()}
        current_habits.update(new_habits)
        current_guardian.habits = current_habits

    session.add(current_guardian)
    session.commit()
    session.refresh(current_guardian)
    return current_guardian

@app.get("/nudges", response_model=List[models.Whisper])
def get_nudges(current_guardian: models.Guardian = Depends(auth.get_current_guardian), session: Session = Depends(get_session)):
    """This endpoint lets a user see all the nudges the scheduler has created for them."""
    nudges = session.exec(select(models.Whisper).where(models.Whisper.guardian_id == current_guardian.id)).all()
    return nudges