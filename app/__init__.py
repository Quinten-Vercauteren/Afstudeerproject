from flask import Flask

# Initialize the Flask application
app = Flask(__name__)

# Load configuration from config.py
app.config.from_object('config')

# Import routes
from app import routes
