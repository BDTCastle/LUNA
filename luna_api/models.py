from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

# The blueprint for our 'guardian' table in the database.
class Guardian(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

# The blueprint for our 'garment' table.
class Garment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    guardian_id: int = Field(foreign_key="guardian.id")
    name: str
    category: str  # e.g., shirt, pants, jacket
    color: str
    weather_suitability: str  # e.g., warm, cold, rainy
    created_at: datetime = Field(default_factory=datetime.utcnow)

# The blueprint for our 'whisper' table.
class Whisper(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    guardian_id: int = Field(foreign_key="guardian.id")
    message: str
    created_at: datetime = Field(default_factory=datetime.utcnow)