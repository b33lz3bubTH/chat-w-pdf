from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 

# --- SQLAlchemy Setup ---
Base = declarative_base()
engine = create_engine("postgresql://postgres:postgres@localhost:5432/chatpdf", echo=False)
SessionLocal = sessionmaker(bind=engine)
