# Module Import
import mariadb
import sys
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLAlchemy setup
Base = declarative_base()

class FilamentData(Base):
    __tablename__ = 'filament_data'
    id = Column(Integer, primary_key=True)
    time = Column(DateTime)
    weight = Column(Integer)
    operation = Column(String)

# Database connection setup
DATABASE_USER_SECRET = "PyMariaDB123"
DATABASE_URL = f"mariadb+mariadbconnector://python:{DATABASE_USER_SECRET}@localhost:3306/filament_weight"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Add Data Function
def add_data(cur, time, weight, operation):
    cur.execute("INSERT INTO filament_weight.filament_data (time, weight, operation) VALUES (?, ?, ?)", 
                (time, weight, operation))

def get_last_data(cur):
    cur.execute("SELECT time FROM filament_weight.filament_data ORDER BY time DESC LIMIT 1") # Get the time of the last row
    return cur.fetchone()[0] # Return the time of the last row


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
