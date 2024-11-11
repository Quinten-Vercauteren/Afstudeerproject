from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config')

# Initialize the database
db = SQLAlchemy(app)

# Import routes and models
from app import routes, models

# Create the database tables if they don't exist
with app.app_context():
    db.create_all()
