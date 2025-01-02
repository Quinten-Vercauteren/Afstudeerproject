import os
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from hardware.loadcell import reinit_hx711
from hardware.camera import Camera  # Import the updated camera module
import config  # Import the config module
from hardware import get_filament_weight, check_octoprint_status
from utils import log_event

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # Use the secret key from config.py
camera = Camera(stream_url="http://octoproject.local/webcam/?action=stream")  # Initialize with stream URL

servicing = False
printer_status = {"status": "unknown"}
state_file_path = "/tmp/printer_state.txt"  # Path to the temporary file

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', servicing=servicing)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Placeholder for actual authentication
        if username == 'admin' and password == 'password':
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/reinit_hx711', methods=['POST'])
def reinit_hx711_route():
    reinit_hx711()
    return redirect(url_for('index'))

@app.route('/service_printer', methods=['POST'])
def service_printer():
    global servicing, printer_status
    print(f"route {servicing}")
    servicing = not servicing
    print(f"after route {servicing}")
    if servicing:
        printer_status["status"] = "Servicing"
        print(f"printer status 1 {printer_status}")
        log_event(f"Servicing state toggled to: {servicing}")
        return jsonify({"servicing": servicing})  # Return JSON response instead of redirecting

    elif not servicing:
        printer_status["status"] = "Inactive"
        log_event(f"Servicing state toggled to: {servicing}")
        return jsonify({"servicing": servicing})  # Return JSON response instead of redirecting

@app.route('/get_servicing_state', methods=['GET'])
def get_servicing_state():
    return jsonify({"servicing": servicing})

@app.route('/octoprint_status', methods=['GET'])
def get_octoprint_status():
    return jsonify(printer_status)

@app.route('/camera_state', methods=['GET'])
def get_camera_state():
    try:
        with open(state_file_path, "r") as state_file:
            state = state_file.read().strip()
        return jsonify({"state": state})
    except FileNotFoundError:
        return jsonify({"state": "unknown"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/filament_weight', methods=['GET'])
def get_filament_weight_route():
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)