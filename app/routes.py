from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from hardware.loadcell import reinit_hx711
from hardware.camera import Camera, update_camera_state  # Import the updated camera module
import threading
from utils import log_event  # <-- Add this import
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
camera = Camera(stream_url="http://octoproject.local/webcam/?action=stream")  # Initialize with stream URL

servicing = False
printer_status = {"status": "unknown"}
state_file_path = os.path.join(os.path.dirname(__file__), "printer_state.txt")  # <-- Define the missing variable

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
    servicing = not servicing  # Toggle servicing state
    if servicing:
        printer_status["status"] = "Servicing"
    else:
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

if __name__ == '__main__':
    threading.Thread(target=update_camera_state, daemon=True).start()  # Start camera state update
    app.run(host='0.0.0.0', port=5001)