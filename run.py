#!/usr/bin/env python3

# Sources:
# ChatGPT model: GPT-4 by OpenAI (03/12/2024)
# Flask documentation: https://flask.palletsprojects.com/
# OctoPrint API documentation: https://docs.octoprint.org/en/master/api/printer.html

from flask import Flask, jsonify
from app.routes import app, servicing  # Import app and servicing flag from app/routes.py
from hardware import get_filament_weight, check_octoprint_status
from utils import log_event
import threading
import time
from hardware.loadcell import setup_hx711
import os
from hardware.camera import update_camera_state  # Import the new function

# Initialize HX711 on startup
setup_hx711()

printer_status = {"status": "unknown"}
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
    global printer_status
    log_event("Hardware monitoring started.")

    try:
        while True:
            if servicing:
                printer_status["status"] = "Servicing"
                log_event("Printer is in servicing mode.")
            else:
                if use_octoprint:
                    status = check_octoprint_status()
                    if status:
                        log_event(f"OctoPrint status: {status}")
                        printer_status["status"] = status
                        if status.lower() == "printing":
                            log_event("Printer started!")
                            weight = get_filament_weight()
                            log_event(f"Filament weight at start: {weight} grams")
                        elif status.lower() == "operational" or status.lower() == "error":
                            log_event("Printer stopped!")
                            weight = get_filament_weight()
                            log_event(f"Filament weight at stop: {weight} grams")
                    else:
                        printer_status["status"] = "Unknown"
                else:
                    try:
                        with open(state_file_path, "r") as state_file:
                            state = state_file.read().strip()
                        printer_status["status"] = state.capitalize()  # Ensure consistent capitalization
                    except FileNotFoundError:
                        printer_status["status"] = "Unknown"
                    except Exception as e:
                        log_event(f"Error reading state file: {str(e)}")
                        printer_status["status"] = "Unknown"
            time.sleep(5)
    except KeyboardInterrupt:
        log_event("Hardware monitoring stopped by user.")

def periodic_octoprint_check():
    """Periodically check if OctoPrint is available."""
    while True:
        if not servicing:
            check_octoprint_connection()
        time.sleep(600)  # Check every 10 minutes

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

if __name__ == "__main__":
    check_octoprint_connection()  # Initial check on startup
    threading.Thread(target=monitor_hardware, daemon=True).start()
    threading.Thread(target=periodic_octoprint_check, daemon=True).start()
    threading.Thread(target=update_camera_state, daemon=True).start()  # Start camera state update
    app.run(host="0.0.0.0", port=5001, debug=True)
