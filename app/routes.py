from flask import Flask, render_template, redirect, url_for, request, session, jsonify
from hardware.loadcell import reinit_hx711
from hardware.Camera import Camera

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a real secret key
camera = Camera()

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

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

@app.route('/start_printer', methods=['POST'])
def start_printer():
    print("Start button pressed")
    return redirect(url_for('index'))

@app.route('/stop_printer', methods=['POST'])
def stop_printer():
    print("Stop button pressed")
    return redirect(url_for('index'))

@app.route('/capture_image', methods=['POST'])
def capture_image():
    print("Capture image button pressed")
    # Placeholder for capturing image functionality
    return redirect(url_for('index'))

@app.route('/motion_status')
def motion_status():
    camera.detect_motion()
    return jsonify({'motion_detected': camera.is_motion_detected()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)