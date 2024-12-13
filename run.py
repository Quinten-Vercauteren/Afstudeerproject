# Sources:
# ChatGPT model: GPT-4 by OpenAI (03/12/2024)
# Flask documentation: https://flask.palletsprojects.com/
# OctoPrint API documentation: https://docs.octoprint.org/en/master/api/printer.html

from flask import Flask
from app import app
from hardware import get_filament_weight, check_octoprint_status#, start_camera, detect_motion
from utils import log_event
import threading
import time

def monitor_hardware():
    """Monitor the printer hardware and track status."""
    log_event("Hardware monitoring started.")

    try:
        while True:
            status = check_octoprint_status()
            if status:
                log_event(f"OctoPrint status: {status}")
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
                print("OctoPrint status not available.")                
                time.sleep(5)
    except KeyboardInterrupt:
        log_event("Hardware monitoring stopped by user.")


if __name__ == "__main__":
    threading.Thread(target=monitor_hardware, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=True)
