from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 

# --- SQLAlchemy Setup ---
Base = declarative_base()
engine = create_engine("sqlite:///tenants.db", echo=False)  # Use SQLite for simplicity; switch to PostgreSQL for production
SessionLocal = sessionmaker(bind=engine)
