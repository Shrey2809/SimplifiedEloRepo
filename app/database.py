from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Path to your existing SQLite database
SQLALCHEMY_DATABASE_URL = "sqlite:///./pickems.db"

# Create the database engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create a sessionmaker factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency to create a session for each request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
