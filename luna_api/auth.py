# File: luna_api/auth.py

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlmodel import Session, select

import models  # <-- FIX #1: Add this missing import
from database import get_session

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "a-very-secret-key-for-luna")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Hashing ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# --- JWT Token Handling ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- The Authentication Dependency ---
def get_current_guardian(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> models.Guardian:
    # <-- FIX #2: Define the exception variable here
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        guardian_id: str = payload.get("sub")
        if guardian_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    guardian = session.exec(select(models.Guardian).where(models.Guardian.id == int(guardian_id))).first()
    if guardian is None:
        raise credentials_exception
    return guardian