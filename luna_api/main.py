# File: luna_api/main.py

# Reminder to self: This is the imports section.
import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Optional, List
from apscheduler.schedulers.background import BackgroundScheduler # <-- NEW: Import the scheduler

# Reminder to self: I'm importing our local modules here.
import auth
import models
import services
from database import engine, get_session
from schemas import GuardianCreate, PreferencesUpdate

# Reminder to self: This is the function the scheduler will run.
def generate_all_nudges():
    """Finds all eligible users and creates a recommendation whisper for them."""
    print("Scheduler is running the daily nudge job...")
    # This function runs in the background, so it needs to create its own DB session.
    with Session(engine) as session:
        # Find all guardians who have nudges enabled and a location set.
        guardians_to_nudge = session.exec(
            select(models.Guardian).where(models.Guardian.enable_nudges == True).where(models.Guardian.location != None)
        ).all()

        for guardian in guardians_to_nudge:
            try:
                recommendation = services.generate_weather_recommendation(city=guardian.location)
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

# Reminder to self: This is the startup event section.
@app.on_event("startup")
def on_startup():
    models.SQLModel.metadata.create_all(engine)
    # <-- NEW: Add and start the scheduler job -->
    # For the hackathon, we run this every 1 minute for easy testing.
    # In a real app, you'd use a cron trigger like: trigger='cron', hour=8
    scheduler.add_job(generate_all_nudges, 'interval', minutes=1)
    scheduler.start()

# <-- NEW: Add a shutdown event to be clean -->
@app.on_event("shutdown")
def on_shutdown():
    scheduler.shutdown()

# Reminder to self: This is the API endpoints section.
@app.post("/signup", response_model=models.Guardian)
def create_guardian(guardian_data: GuardianCreate, session: Session = Depends(get_session)):
    # ... (existing signup code, no changes)
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
    # ... (existing login code, no changes)
    guardian = session.exec(select(models.Guardian).where(models.Guardian.email == form_data.username)).first()
    if not guardian or not auth.verify_password(form_data.password, guardian.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = auth.create_access_token(data={"sub": guardian.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/me", response_model=models.Guardian)
def read_users_me(current_guardian: models.Guardian = Depends(auth.get_current_guardian)):
    return current_guardian

@app.get("/recommendation")
def get_recommendation(current_guardian: models.Guardian = Depends(auth.get_current_guardian)):
    # ... (existing recommendation code, no changes)
    if not current_guardian.location:
        raise HTTPException(
            status_code=400, 
            detail="No location found. Please set one."
        )
    recommendation = services.generate_weather_recommendation(city=current_guardian.location)
    return {"recommendation": recommendation}

@app.patch("/preferences", response_model=models.Guardian)
def update_preferences(
    preferences: PreferencesUpdate,
    current_guardian: models.Guardian = Depends(auth.get_current_guardian),
    session: Session = Depends(get_session)
):
    # ... (existing preferences code, no changes)
    update_data = preferences.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(current_guardian, key, value)
    session.add(current_guardian)
    session.commit()
    session.refresh(current_guardian)
    return current_guardian

# <-- ENTIRELY NEW SECTION: The Nudges Endpoint -->
@app.get("/nudges", response_model=List[models.Whisper])
def get_nudges(current_guardian: models.Guardian = Depends(auth.get_current_guardian), session: Session = Depends(get_session)):
    """Reminder to self: This endpoint lets a user see all the nudges the scheduler has created for them."""
    nudges = session.exec(select(models.Whisper).where(models.Whisper.guardian_id == current_guardian.id)).all()
    return nudges