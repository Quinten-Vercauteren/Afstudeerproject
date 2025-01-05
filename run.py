# Sources:
# ChatGPT model: GPT-4 by OpenAI (03/12/2024)
# Flask documentation: https://flask.palletsprojects.com/
# OctoPrint API documentation: https://docs.octoprint.org/en/master/api/printer.html

from app.routes import app  # Import app from app/routes.py
from hardware.loadcell import setup_hx711, get_filament_weight  # Import setup_hx711 and get_filament_weight
from hardware.camera import update_camera_state, camera_motion_detected, camera_state_queue  # Import the new function and shared variables
from hardware.octoprintstatus import check_octoprint_status  # Import check_octoprint_status
from utils import log_event
import threading
import time
import os
import queue
import app.shared_state as shared_state  # Import shared state module


# Initialize HX711 on startup
setup_hx711()

# Initialize the camera state queue with "Inactive"
camera_state_queue.put("Inactive")

use_octoprint = False
print("---")
log_event(shared_state.servicing)
print("---")
def check_octoprint_connection():
    """Check if OctoPrint is available."""
    global use_octoprint
    try:
        octostatus = check_octoprint_status()
        if (octostatus):
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
    log_event("Hardware monitoring started.")

    try:
        while True:
            print('---------------------------------------------------------------------------------------------')
            if shared_state.servicing:
                shared_state.printer_status["status"] = "Servicing"
                log_event("Printer is in servicing mode.")
            elif use_octoprint:
                octoprint_status = check_octoprint_status()
                if octoprint_status:
                    shared_state.printer_status["status"] = octoprint_status
                    log_event(f"OctoPrint status: {octoprint_status}")
                else:
                    shared_state.printer_status["status"] = "Unknown"
                    log_event("Failed to get OctoPrint status.")
            else:
                try:
                    camera_state = camera_state_queue.get_nowait()
                    shared_state.printer_status["status"] = camera_state  # Use the global camera_state variable
                    log_event(f"Camera state: {camera_state}")
                except queue.Empty:
                    log_event("No new camera state available.")
                log_event(f"Current state: {shared_state.printer_status['status']}")
            weight = get_filament_weight()  # Get the current weight
            log_event(f"Current filament weight: {weight} grams")
            
            time.sleep(5)
    except KeyboardInterrupt:
        log_event("Hardware monitoring stopped by user.")

def periodic_octoprint_check():
    """Periodically check if OctoPrint is available."""
    while True:
        if shared_state.servicing == False:
            check_octoprint_connection()
        # Initialize the camera state queue with "Inactive"
        camera_state_queue.put("Inactive")
        time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    check_octoprint_connection()  # Initial check on startup
    threading.Thread(target=monitor_hardware, daemon=True).start()
    threading.Thread(target=periodic_octoprint_check, daemon=True).start()
    threading.Thread(target=update_camera_state, daemon=True).start()  # Start camera state update
    app.run(host="0.0.0.0", port=5001, debug=True)
