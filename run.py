#!/usr/bin/env python3

# Sources:
# ChatGPT model: GPT-4 by OpenAI (03/12/2024)
# Flask documentation: https://flask.palletsprojects.com/
# OctoPrint API documentation: https://docs.octoprint.org/en/master/api/printer.html

from flask import Flask, jsonify
from app.routes import app  # Import app from app/routes.py
from hardware import get_filament_weight, check_octoprint_status
from utils import log_event
import threading
import time
from hardware.loadcell import setup_hx711

# Initialize HX711 on startup
setup_hx711()

printer_status = {"status": "unknown"}

def monitor_hardware():
    """Monitor the printer hardware and track status."""
    global printer_status
    log_event("Hardware monitoring started.")

    try:
        while True:
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
                time.sleep(5)
            else:
                printer_status["status"] = "unknown"
                time.sleep(5)
    except KeyboardInterrupt:
        log_event("Hardware monitoring stopped by user.")

@app.route('/printer_status', methods=['GET'])
def get_printer_status():
    return jsonify(printer_status)

if __name__ == "__main__":
    threading.Thread(target=monitor_hardware, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=True)
