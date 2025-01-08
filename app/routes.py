from flask import Flask, render_template, redirect, url_for, request, session as flask_session, jsonify
from hardware.loadcell import reinit_hx711, get_filament_weight  # Import get_filament_weight
from hardware.camera import Camera, update_camera_state, camera_state_queue  # Import the updated camera module and camera_state_queue
import threading
from utils import log_event
from config import SECRET_KEY
import os
from models import FilamentData, SessionLocal  # Import the FilamentData model and SessionLocal
import shared_state
from shared_state import get_printer_status, set_printer_status, get_servicing_state, toggle_servicing_state

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Replace with a real secret key
camera = Camera(stream_url="http://octoproject.local/webcam/?action=stream")  # Initialize with stream URL

# Create a session
db_session = SessionLocal()

@app.route('/')
def index():
    """Render the main control panel page."""
    if 'username' not in flask_session:
        return redirect(url_for('login'))
    return render_template('index.html', servicing=shared_state.get_servicing_state())

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Placeholder for actual authentication
        if username == 'admin' and password == 'password':
            flask_session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Handle user logout."""
    flask_session.pop('username', None)
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
    
    # Retrieve all filament data from the database
    session = SessionLocal()
    filament_data = session.query(FilamentData).all()
    session.close()
    
    return render_template('database.html', filament_data=filament_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)