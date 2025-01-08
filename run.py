# Sources:
# ChatGPT model: GPT-4 by OpenAI (03/12/2024)
# Flask documentation: https://flask.palletsprojects.com/
# OctoPrint API documentation: https://docs.octoprint.org/en/master/api/printer.html
# Maria DB: https://mariadb.com/docs/server/connect/programming-languages/python/dml/

from app.routes import app  # Import app from app/routes.py
from hardware.loadcell import setup_hx711, get_filament_weight  # Import setup_hx711 and get_filament_weight
from hardware.camera import update_camera_state, camera_motion_detected, camera_state_queue  # Import the new function and shared variables
from hardware.octoprintstatus import check_octoprint_status  # Import check_octoprint_status
from utils import log_event
import threading
import time
import os
import queue
import shared_state  # Import shared state module without aliasing
from models import add_data, conn, cur, SessionLocal  # Import add_data, conn, cur, and SessionLocal from models
from shared_state import get_printer_status, set_printer_status, get_servicing_state, toggle_servicing_state, get_last_known_status, set_last_known_status

# Initialize HX711 on startup
setup_hx711()

# Initialize the camera state queue with "Inactive"
camera_state_queue.put("Inactive")

current_status = "Unknown"
last_known_status = "Unknown"

use_octoprint = False

inactiveSwitch = True
last_insertion_time = 0
last_printing_time = 0  # Track the last time the state was changed to "Printing"

class PrinterState:
    def __init__(self):
        current_state = get_printer_status()["status"]
        self.last_known_status = get_last_known_status()  # Initialize with last known status from JSON
        self.inactiveSwitch = True if current_state != "Printing" else False  # Set based on current state
        self.last_insertion_time = 0
        self.last_printing_time = 0

def db_trigger(current_status, printer_state):
    print("------------------db_trigger-------------")
    current_time = time.time()
    print(printer_state.last_known_status)
    if current_status != printer_state.last_known_status:
        print(f"Status changed from {printer_state.last_known_status} to {current_status}")
        if current_status == "Printing" and printer_state.inactiveSwitch:
            printer_state.inactiveSwitch = False
            if current_time - printer_state.last_insertion_time >= 10 and current_time - printer_state.last_printing_time >= 10:
                weight = get_filament_weight()
                log_event(f"Current filament weight: {weight} grams")
                operation = "Started printing"
                save_weight_data(weight, operation)
                printer_state.last_insertion_time = current_time
                printer_state.last_printing_time = current_time
                log_event("The printer started printing.")
                print("The printer started printing.")
        elif current_status != "Printing" and not printer_state.inactiveSwitch:
            printer_state.inactiveSwitch = True
            if current_time - printer_state.last_insertion_time >= 10:
                weight = get_filament_weight()
                operation = "Stopped printing"
                save_weight_data(weight, operation)
                printer_state.last_insertion_time = current_time
                log_event("The printer stopped printing.")
                print("The printer stopped printing.")
        printer_state.last_known_status = current_status
        set_last_known_status(current_status)  # Write last known status to JSON
    print(printer_state.last_known_status)

def save_weight_data(weight, operation):
    """Save the weight data in MariaDB."""
    time_str = time.strftime('%Y-%m-%d %H:%M:%S')  # Get current time in required format
    add_data(cur, time_str, weight, operation)
    log_event(f"Weight data saved: {weight} grams, {operation}")

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
    printer_state = PrinterState()  # Initialize printer state with current status
    log_event("Hardware monitoring started.")
    try:
        while True:
            print('---------------------------------------------------------------------------------------------')
            print(f"Checking servicing state: {get_servicing_state()}")
            if get_servicing_state():
                if get_printer_status()["status"] != "Servicing":
                    set_printer_status({"status": "Servicing"})
                    log_event("Printer is in servicing mode.")
            elif use_octoprint:
                octoprint_status = check_octoprint_status()
                print(f"OctoPrint status: {octoprint_status}")
                if octoprint_status and get_printer_status()["status"] != octoprint_status:
                    set_printer_status({"status": octoprint_status})
                    log_event(f"OctoPrint status: {octoprint_status}")
                elif not octoprint_status and get_printer_status()["status"] != "Unknown":
                    set_printer_status({"status": "Unknown"})
                    log_event("Failed to get OctoPrint status.")
            else:
                try:
                    camera_state = camera_state_queue.get_nowait()
                    print(f"Camera state: {camera_state}")
                    if get_printer_status()["status"] != camera_state:
                        set_printer_status({"status": camera_state})
                        log_event(f"Camera state: {camera_state}")
                except queue.Empty:
                    log_event("No new camera state available.")
            
            current_status = get_printer_status()["status"]
            log_event(f"Current state: {current_status}")
            print(f"Current state: {current_status}")
            print('--------------------------------------------------------------------------------------------*')
            
            db_trigger(current_status, printer_state)
            
            time.sleep(5)
    except KeyboardInterrupt:
        log_event("Hardware monitoring stopped by user.")

def periodic_octoprint_check():
    """Periodically check if OctoPrint is available."""
    while True:
        if get_servicing_state() == False:
            check_octoprint_connection()
        # Initialize the camera state queue with "Inactive"
        camera_state_queue.put("Inactive")
        time.sleep(600)  # Check every 10 minutes

if __name__ == "__main__":
    threading.Thread(target=periodic_octoprint_check, daemon=True).start()
    threading.Thread(target=monitor_hardware, daemon=True).start()
    threading.Thread(target=update_camera_state, daemon=True).start()  # Start camera state update
    app.run(host="0.0.0.0", port=5001, debug=True)
