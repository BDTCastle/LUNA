# Models: Define database tables for users (Guardian), wardrobe items (Garment), and nudges (Whisper).
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Guardian(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    location: Optional[str] = Field(default=None)  # User's city, e.g., "London"
    enable_nudges: bool = Field(default=True)  # Toggle for nudges
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Garment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    guardian_id: int = Field(foreign_key="guardian.id")
    name: str
    category: str
    color: str
    weather_suitability: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Whisper(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    guardian_id: int = Field(foreign_key="guardian.id")
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)