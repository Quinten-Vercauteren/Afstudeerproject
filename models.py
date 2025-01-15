# Documentation and sources:
# SQLAlchemy: https://docs.sqlalchemy.org/
# MariaDB: https://mariadb.com/kb/en/mariadb-python-connector/
# Python: https://www.python.org/doc/
# ChatGPT model: OpenAI GPT-4 (2024) - https://chatgpt.com/

import mariadb
import sys
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_USER_SECRET, DATABASE_URL

# SQLAlchemy setup
Base = declarative_base()

class FilamentData(Base):
    __tablename__ = 'filament_data'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    weight = Column(Integer)
    operation = Column(String)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)

# Database connection setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Add Data Function
def add_data(cur, time, weight, operation):
    cur.execute("INSERT INTO filament_weight.filament_data (time, weight, operation) VALUES (?, ?, ?)", 
                (time, weight, operation))

def get_last_data(cur):
    cur.execute("SELECT time FROM filament_weight.filament_data ORDER BY time DESC LIMIT 1") # Get the time of the last row
    return cur.fetchone()[0] # Return the time of the last row

def add_user(username, password, role):
    """Add a new user to the database."""
    session = SessionLocal()
    user = User(username=username, password=password, role=role)
    session.add(user)
    session.commit()
    session.close()

def get_user(username):
    """Retrieve a user from the database by username."""
    session = SessionLocal()
    user = session.query(User).filter_by(username=username).first()
    session.close()
    return user

# Instantiate Connection
try:
   conn = mariadb.connect(
      host="localhost",
      port=3306,
      user="python",
      password=DATABASE_USER_SECRET,  # Ensure the password is correct
      autocommit=True)
except mariadb.Error as e:
    print(f"Error connecting to the database: {e}")
    sys.exit(1)


# Instantiate Cursor
cur = conn.cursor()
