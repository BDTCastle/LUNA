# File: luna_api/schemas.py

from sqlmodel import SQLModel
from typing import Optional

# --- Guardian Schemas ---
class GuardianCreate(SQLModel):
    email: str
    password: str
    location: Optional[str] = None

# --- Preferences Schemas ---
class PreferencesUpdate(SQLModel):
    location: Optional[str] = None
    enable_nudges: Optional[bool] = None