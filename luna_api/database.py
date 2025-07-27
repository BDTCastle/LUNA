# File: luna_api/database.py

import os
from sqlmodel import create_engine, Session

# Get the database URL from the environment variable we set in docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL")

# The engine is the central point of communication with the database
# echo=True will print all the SQL statements to the console, which is great for debugging.
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """Dependency to get a database session for each request."""
    with Session(engine) as session:
        yield session