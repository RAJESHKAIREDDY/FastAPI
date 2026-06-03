from sqlalchemy import create_engine  # create_engine builds the connection to the database
from sqlalchemy.ext.declarative import declarative_base  # declarative_base provides the base class for ORM models
from sqlalchemy.orm import sessionmaker  # sessionmaker creates a factory for database session objects

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"  # SQLite DB stored as a file in the current directory

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})  # check_same_thread=False allows SQLite to be used across multiple threads (required for FastAPI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # autocommit=False means changes must be explicitly committed; autoflush=False prevents premature writes

Base = declarative_base()  # all ORM model classes will inherit from this Base to be recognized by SQLAlchemy
