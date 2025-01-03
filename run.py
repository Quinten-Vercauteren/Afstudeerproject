#!/usr/bin/env python3

# Sources:
# ChatGPT model: GPT-4 by OpenAI (03/12/2024)
# Flask documentation: https://flask.palletsprojects.com/
# OctoPrint API documentation: https://docs.octoprint.org/en/master/api/printer.html

from app.routes import app, servicing, printer_status  # Import app, servicing flag, and printer_status from app/routes.py
from hardware import get_filament_weight, check_octoprint_status
from utils import log_event
import threading
import time
from hardware.loadcell import setup_hx711
import os
from hardware.camera import update_camera_state, camera_motion_detected  # Import the new function and shared variable

# Initialize HX711 on startup
setup_hx711()

state_file_path = "/tmp/printer_state.txt"  # Path to the temporary file
use_octoprint = False

def check_octoprint_connection():
    """Check if OctoPrint is available."""
    global use_octoprint
    try:
        status = check_octoprint_status()
        if status:
            use_octoprint = True
            log_event("OctoPrint connection established.")
        else:
            use_octoprint = False
            log_event("OctoPrint connection failed. Using motion detection.")
    except Exception as e:
        use_octoprint = False
        log_event(f"Error checking OctoPrint connection: {str(e)}")

def monitor_hardware():
    """Monitor the printer hardware and track status."""
    global printer_status, servicing  # Ensure servicing is updated
    log_event("Hardware monitoring started.")

    try:
        while True:
            if servicing:
                printer_status["status"] = "Servicing"
                log_event("Printer is in servicing mode.")
            elif camera_motion_detected:
                printer_status["status"] = "Printing"
                log_event("Printer is printing.")
            else:
                printer_status["status"] = "Inactive"
                log_event("Printer is inactive.")

            log_event(f"Current state: {printer_status['status']}")
            time.sleep(5)
    except KeyboardInterrupt:
        log_event("Hardware monitoring stopped by user.")

def periodic_octoprint_check():
    """Periodically check if OctoPrint is available."""
    while True:
        if not servicing:
            check_octoprint_connection()
        time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    check_octoprint_connection()  # Initial check on startup
    threading.Thread(target=monitor_hardware, daemon=True).start()
    threading.Thread(target=periodic_octoprint_check, daemon=True).start()
    threading.Thread(target=update_camera_state, daemon=True).start()  # Start camera state update
    app.run(host="0.0.0.0", port=5001, debug=True)
