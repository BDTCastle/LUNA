# Imports Section: Note to self - These are all the libraries I need for the app. FastAPI for web routes, SQLModel for database, auth for password hashing, requests for weather API, random for varied responses, and JWT for user authentication.
import os
from fastapi import FastAPI, Depends, HTTPException, Header, BackgroundTasks
from sqlmodel import create_engine, SQLModel, Session, select
from models import Guardian, Whisper
import auth
from datetime import datetime, timedelta
from jose import jwt, JWTError
import requests
from config import OPENWEATHER_API_KEY
import random
from typing import Optional

# Pydantic Models Section: Note to self - These define the shape of data from user requests. GuardianCreate for signup (email, password, etc.), PreferencesUpdate for toggling features like nudges.
class GuardianCreate(SQLModel):
    email: str  # Must be a valid email string
    password: str  # Password to hash and store
    location: Optional[str] = None  # Optional city, e.g., "London"
    enable_nudges: Optional[bool] = True  # Optional toggle for nudges, defaults to True

class PreferencesUpdate(SQLModel):
    enable_nudges: Optional[bool] = None  # Optional boolean to update nudge setting

# Database Setup Section: Note to self - This connects to the PostgreSQL database in Docker. The engine is the connection, and get_session ensures safe database access for each request.
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://luna_user:luna_password@db:5432/luna_db")
engine = create_engine(DATABASE_URL)

def get_session():
    """Note to self: This provides a database session for endpoints, auto-closing to prevent leaks."""
    with Session(engine) as session:
        yield session

# JWT Configuration Section: Note to self - These settings control user authentication tokens. The secret key signs tokens, the algorithm secures them, and the expiry time limits their lifespan.
SECRET_KEY = "your-secret-key"  # Reminder: Change to a secure random string in production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# FastAPI App Setup Section: Note to self - This creates the main app instance that handles all API routes and requests.
app = FastAPI(title="L.U.N.A. - Lifestyle Utility & Nurturing Assistant")

# Startup Event Section: Note to self - This runs when the app starts, creating database tables (Guardian, Whisper) if they don’t exist yet.
@app.on_event("startup")
def on_startup():
    """Note to self: This creates tables in the database when the app starts."""
    SQLModel.metadata.create_all(engine)
    print("Database initialized")

# API Endpoints Section: Note to self - These are the routes users hit, like signing up, logging in, getting outfit recommendations, or toggling nudges. Each handles specific app features.
@app.get("/")
def read_root():
    """Note to self: Simple welcome endpoint to check if the app is running."""
    return {"message": "Welcome to L.U.N.A.!"}

@app.post("/signup", response_model=Guardian, status_code=201)
def create_guardian(guardian_data: GuardianCreate, session: Session = Depends(get_session)):
    """Note to self: This handles user signup. It checks for duplicate emails, hashes the password, and saves the user with location and nudge preference."""
    existing_guardian = session.exec(
        select(Guardian).where(Guardian.email == guardian_data.email)
    ).first()
    if existing_guardian:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(guardian_data.password)
    db_guardian = Guardian(
        email=guardian_data.email,
        hashed_password=hashed_password,
        location=guardian_data.location,
        enable_nudges=guardian_data.enable_nudges
    )

    session.add(db_guardian)
    session.commit()
    session.refresh(db_guardian)

    return db_guardian

@app.post("/login")
def login(guardian_data: GuardianCreate, session: Session = Depends(get_session)):
    """Note to self: This logs in users, verifies their password, and returns a JWT token for secure access."""
    guardian = session.exec(
        select(Guardian).where(Guardian.email == guardian_data.email)
    ).first()
    if not guardian or not auth.verify_password(guardian_data.password, guardian.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": str(guardian.id), "email": guardian.email, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}

@app.get("/recommendation")
def get_recommendation(gender: str, city: Optional[str] = None, authorization: Optional[str] = Header(None), session: Session = Depends(get_session)):
    """Note to self: This generates outfit recommendations based on weather, gender, and user’s stored location (if logged in). It uses OpenWeatherMap for weather data."""
    if authorization and authorization.startswith("Bearer "):
        token = authorization.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            guardian_id = int(payload.get("sub"))
            guardian = session.exec(select(Guardian).where(Guardian.id == guardian_id)).first()
            if guardian and guardian.location:
                city = guardian.location
        except JWTError:
            pass

    if not city:
        raise HTTPException(status_code=400, detail="City not provided and no location in user profile")

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(weather_url)
    if response.status_code != 200:
        print(f"Weather API error: Status {response.status_code}, Response: {response.text}")
        raise HTTPException(status_code=400, detail="Invalid city or weather API error")

    weather_data = response.json()
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    condition = weather_data['weather'][0]['main'].lower()

    if temp > 25:
        base = "warm"
        day = random.choice(["sunny and hot day", "warm weather outside"])
    elif 15 < temp <= 25:
        base = "mild"
        day = random.choice(["pleasant day", "comfortable temperature"])
    else:
        base = "cold"
        day = random.choice(["chilly day", "cool weather"])

    if gender.lower() == "female":
        outfit = random.choice(["a skirt or dress with a blouse", "a sundress or light top with skirts"])
        caveat = "Shorts or jeans would be comfortable too."
    else:
        outfit = random.choice(["shorts or pants with a t-shirt", "jeans and a casual shirt"])
        caveat = "Jeans or shorts would be comfortable too."

    humidity_advice = "High humidity, so go for breathable fabrics." if humidity > 70 else ""
    wind_advice = "Windy, so layer up with a windbreaker." if wind_speed > 10 else ""
    night_caveat = "but it may be cold tonight, so take a light jacket if you'll be out late" if temp < 20 else ""

    greeting = random.choice(["Hey!", "Hi there!", "Good day!"])
    recommendation = f"{greeting} It's {base} in {city} ({temp}°C, {condition}). For today's {day}, you can wear {outfit}. {caveat} {humidity_advice} {wind_advice} It's {condition}, so {night_caveat}."

    return {"recommendation": recommendation}

@app.patch("/preferences")
def update_preferences(preferences: PreferencesUpdate, authorization: str = Header(...), session: Session = Depends(get_session)):
    """Note to self: This lets users toggle features like nudges. It requires a JWT token to identify the user and updates their preferences."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        guardian_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    guardian = session.exec(select(Guardian).where(Guardian.id == guardian_id)).first()
    if not guardian:
        raise HTTPException(status_code=404, detail="User not found")

    if preferences.enable_nudges is not None:
        guardian.enable_nudges = preferences.enable_nudges

    session.add(guardian)
    session.commit()
    session.refresh(guardian)

    return {"enable_nudges": guardian.enable_nudges}

# Note to self: This endpoint lists all saved nudges (Whispers) for the authenticated user, showing their history of recommendations.
@app.get("/nudges", response_model=list[Whisper])
def list_nudges(authorization: str = Header(...), session: Session = Depends(get_session)):
    """Returns a list of all saved nudges (Whispers) for the authenticated user."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        guardian_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    guardian = session.exec(select(Guardian).where(Guardian.id == guardian_id)).first()
    if not guardian:
        raise HTTPException(status_code=404, detail="User not found")

    whispers = session.exec(select(Whisper).where(Whisper.guardian_id == guardian_id)).all()
    return whispers

# Note to self: This endpoint creates a new nudge (Whisper) with a recommendation if nudges are enabled, using POST for RESTful creation.
@app.post("/nudges")
def create_nudge(nudge_data: dict, background_tasks: BackgroundTasks, authorization: str = Header(...), session: Session = Depends(get_session)):
    """Creates a nudge (Whisper) based on recommendation if nudges are enabled, using city and gender from the request body."""
    city = nudge_data.get("city")
    gender = nudge_data.get("gender")
    if not city or not gender:
        raise HTTPException(status_code=400, detail="City and gender are required")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        guardian_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    guardian = session.exec(select(Guardian).where(Guardian.id == guardian_id)).first()
    if not guardian:
        raise HTTPException(status_code=404, detail="User not found")

    if not guardian.enable_nudges:
        return {"message": "Nudges are disabled. Enable them in preferences."}

    weather_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(weather_url)
    if response.status_code != 200:
        print(f"Weather API error: Status {response.status_code}, Response: {response.text}")
        raise HTTPException(status_code=400, detail="Invalid city or weather API error")

    weather_data = response.json()
    temp = weather_data['main']['temp']
    humidity = weather_data['main']['humidity']
    wind_speed = weather_data['wind']['speed']
    condition = weather_data['weather'][0]['main'].lower()

    if temp > 25:
        base = "warm"
        day = random.choice(["sunny and hot day", "warm weather outside"])
    elif 15 < temp <= 25:
        base = "mild"
        day = random.choice(["pleasant day", "comfortable temperature"])
    else:
        base = "cold"
        day = random.choice(["chilly day", "cool weather"])

    if gender.lower() == "female":
        outfit = random.choice(["a skirt or dress with a blouse", "a sundress or light top with skirts"])
        caveat = "Shorts or jeans would be comfortable too."
    else:
        outfit = random.choice(["shorts or pants with a t-shirt", "jeans and a casual shirt"])
        caveat = "Jeans or shorts would be comfortable too."

    humidity_advice = "High humidity, so go for breathable fabrics." if humidity > 70 else ""
    wind_advice = "Windy, so layer up with a windbreaker." if wind_speed > 10 else ""
    night_caveat = "but it may be cold tonight, so take a light jacket if you'll be out late" if temp < 20 else ""

    greeting = random.choice(["Hey!", "Hi there!", "Good day!"])
    recommendation = f"{greeting} It's {base} in {city} ({temp}°C, {condition}). For today's {day}, you can wear {outfit}. {caveat} {humidity_advice} {wind_advice} It's {condition}, so {night_caveat}."

    def save_whisper():
        """Note to self: This saves the recommendation as a Whisper in the background, so it doesn’t slow down the response."""
        whisper = Whisper(guardian_id=guardian_id, message=recommendation)
        with Session(engine) as session:
            session.add(whisper)
            session.commit()

    background_tasks.add_task(save_whisper)

    return {"recommendation": recommendation}