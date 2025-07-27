# Reminder to self: This is the models section. These define the database tables for L.U.N.A., like users (Guardian), wardrobe items (Garment), and nudges (Whisper). I use SQLModel to map Python classes to database tables.
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from sqlalchemy import JSON, Column  # Reminder: Import JSON from sqlalchemy for JSONB fields in PostgreSQL

class Guardian(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-generated ID
    email: str = Field(unique=True, index=True)  # Unique email with index for fast lookup
    hashed_password: str  # Hashed password for security
    location: Optional[str] = Field(default=None)  # Optional city, e.g., "London"
    enable_nudges: bool = Field(default=True)  # Toggle for general nudges
    habits: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # JSON field for habit settings, e.g., {"water": {"enabled": true, "interval_hours": 4}}
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Timestamp when created

class Garment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-generated ID
    guardian_id: int = Field(foreign_key="guardian.id")  # Links to Guardian
    name: str  # Item name, e.g., "Blue T-shirt"
    category: str  # Item type, e.g., "shirt"
    color: str  # Item color, e.g., "blue"
    weather_suitability: str  # Suitable weather, e.g., "warm"
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Timestamp when created

class Whisper(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)  # Auto-generated ID
    guardian_id: int = Field(foreign_key="guardian.id")  # Links to Guardian
    message: str  # Nudge message, e.g., "Time to drink water!"
    created_at: datetime = Field(default_factory=datetime.utcnow)  # Timestamp when created