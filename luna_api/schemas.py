# File: luna_api/schemas.py
# Reminder to self: Defines request schemas

from sqlmodel import SQLModel
from typing import Optional, Dict

# --- Guardian Schemas ---
class GuardianCreate(SQLModel):
    email: str
    password: str
    location: Optional[str] = None
# --- Habit Schemas ---
class HabitSettings(SQLModel):
    enabled: bool
    interval_hours: float

# --- Preferences Schemas ---
class PreferencesUpdate(SQLModel):
    location: Optional[str] = None
    enable_nudges: Optional[bool] = None
    habits: Optional[Dict[str, HabitSettings]] = None