import os
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from hardware.loadcell import reinit_hx711
from hardware.camera import Camera  # Import the updated camera module
import config  # Import the config module

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # Use the secret key from config.py
camera = Camera(stream_url="http://octoproject.local/webcam/?action=stream")  # Initialize with stream URL

servicing = False

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
    global servicing
    servicing = not servicing  # Toggle servicing state
    print(f"Servicing state toggled to: {servicing}")
    return redirect(url_for('index'))

@app.route('/get_servicing_state', methods=['GET'])
def get_servicing_state():
    return jsonify({"servicing": servicing})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)