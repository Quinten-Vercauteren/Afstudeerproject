# Flask Application Routes

# This module contains the route definitions for the Flask web application.

# Documentation and sources:
# Flask: https://flask.palletsprojects.com/
# SQLAlchemy: https://www.sqlalchemy.org/
# Jinja2: https://jinja.palletsprojects.com/
# Flask-Login: https://flask-login.readthedocs.io/
# ChatGPT model: OpenAI GPT-4 (2024) - https://chatgpt.com/


from flask import Flask, render_template, redirect, url_for, request, session as flask_session, jsonify
from hardware.loadcell import reinit_hx711, get_filament_weight  # Import get_filament_weight
from hardware.camera import Camera, update_camera_state, camera_state_queue  # Import the updated camera module and camera_state_queue
import threading
from utils import log_event
from config import SECRET_KEY
import os
from models import FilamentData, SessionLocal, User  # Import the FilamentData model, SessionLocal, and User
import shared_state
from shared_state import get_printer_status, set_printer_status, get_servicing_state, toggle_servicing_state
from auth import authenticate_user, create_user  # Import authentication functions

app = Flask(__name__)
app.secret_key = SECRET_KEY
camera = Camera(stream_url="http://octoproject.local/webcam/?action=stream")  # Initialize with stream URL

# Create a session
db_session = SessionLocal()

@app.route('/')
def index():
    """Render the main control panel page."""
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    if flask_session['role'] == 'data_analyst':
        return redirect(url_for('database'))
    return render_template('index.html', servicing=shared_state.get_servicing_state())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = authenticate_user(username, password)
        if user:
            flask_session['username'] = user.username
            flask_session['role'] = user.role
            if user.role == 'data_analyst':
                return redirect(url_for('database'))
            return redirect(url_for('index'))
        else:
            error = 'Invalid credentials. Please try again.'
    return render_template('login.html', error=error)

@app.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    flask_session.pop('username', None)
    flask_session.pop('role', None)
    return redirect(url_for('login'))

@app.route('/reinit_hx711', methods=['POST'])
def reinit_hx711_route():
    """Reinitialize and tare the HX711 sensor."""
    reinit_hx711()
    return redirect(url_for('index'))

@app.route('/service_printer', methods=['POST'])
def service_printer():
    """Toggle the servicing state of the printer."""
    toggle_servicing_state()
    set_printer_status({"status": "Inactive"})  # Reset printer status
    log_event(f"Servicing state toggled to: {get_servicing_state()}")
    return redirect(url_for('index'))

@app.route('/printer_status', methods=['GET'])
def get_printer_status_route():
    """Get the current state of the printer."""
    try:
        return jsonify(get_printer_status())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/filament_weight', methods=['GET'])
def get_filament_weight_route():
    """Get the current weight of the filament."""
    try:
        weight = get_filament_weight()
        if weight is not None:
            return jsonify({"weight": weight})
        else:
            log_event("Failed to retrieve weight: weight is None")
            return jsonify({"error": "Failed to retrieve weight"}), 500
    except Exception as e:
        log_event(f"Exception in get_filament_weight_route: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/get_servicing_state', methods=['GET'])
def get_servicing_state_route():
    """Get the current servicing state of the printer."""
    try:
        return jsonify({"servicing": get_servicing_state()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/database')
def database():
    """Render the database page showing filament data."""
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    if flask_session['role'] not in ['admin', 'data_analyst', 'manager']:
        return 'Access denied', 403
    
    # Retrieve all filament data from the database
    session = SessionLocal()
    filament_data = session.query(FilamentData).all()
    session.close()
    
    return render_template('database.html', filament_data=filament_data)

@app.route('/printer_control')
def printer_control():
    """Render the printer control panel page."""
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    if flask_session['role'] not in ['admin', 'printer_operator', 'manager']:
        return 'Access denied', 403
    
    return render_template('index.html', servicing=shared_state.get_servicing_state())

@app.route('/accounts')
def accounts():
    """Render the accounts page showing all users and their roles."""
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    if flask_session['role'] != 'admin':
        return 'Access denied', 403
    
    # Retrieve all users from the database
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    
    return render_template('accounts.html', users=users)

@app.route('/add_user', methods=['POST'])
def add_user_route():
    """Add a new user."""
    if 'username' not in flask_session or flask_session['role'] != 'admin':
        return 'Access denied', 403
    
    username = request.form['username']
    password = request.form['password']
    role = request.form['role']
    create_user(username, password, role)
    return redirect(url_for('accounts'))

@app.route('/remove_user/<int:user_id>', methods=['POST'])
def remove_user_route(user_id):
    """Remove a user."""
    if 'username' not in flask_session or flask_session['role'] != 'admin':
        return 'Access denied', 403
    
    session = SessionLocal()
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()
    return redirect(url_for('accounts'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)