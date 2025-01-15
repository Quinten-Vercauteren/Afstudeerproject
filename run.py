# Documentation and sources:
# Flask: https://flask.palletsprojects.com/
# OctoPrint API: https://docs.octoprint.org/en/master/api/printer.html
# MariaDB: https://mariadb.com/docs/server/connect/programming-languages/python/dml/
# HX711: https://github.com/tatobari/hx711py
# OpenCV: https://docs.opencv.org/
# ChatGPT model: OpenAI GPT-4 (2024) - https://chatgpt.com/

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
from models import add_data, conn, cur, SessionLocal, get_last_data  # Import add_data, conn, cur, SessionLocal, and get_last_data from models
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
    current_time = time.time()

    if current_status != printer_state.last_known_status:
        printer_state.last_known_status = current_status
        set_last_known_status(current_status)
        if current_status == "Printing" and printer_state.inactiveSwitch:
            printer_state.inactiveSwitch = False
            if current_time - printer_state.last_insertion_time >= 100 and current_time - printer_state.last_printing_time >= 100:
                weight = get_filament_weight()
                log_event(f"Current filament weight: {weight} grams")
                operation = "Started printing"
                save_weight_data(weight, operation)
                printer_state.last_insertion_time = current_time
                printer_state.last_printing_time = current_time
                log_event("The printer started printing.")
        elif current_status != "Printing" and not printer_state.inactiveSwitch:
            printer_state.inactiveSwitch = True
            if current_time - printer_state.last_insertion_time >= 30:
                weight = get_filament_weight()
                log_event(f"Current filament weight: {weight} grams")
                operation = "Stopped printing"
                save_weight_data(weight, operation)
                printer_state.last_insertion_time = current_time
                log_event("The printer stopped printing.")
    print(printer_state.last_known_status)

def save_weight_data(weight, operation):
    """Save the weight data in MariaDB."""
    time_str = time.strftime('%Y-%m-%d %H:%M:%S')  # Get current time in required format
    last_insertion_time_dt = get_last_data(cur)  # Get the last insertion time as a datetime object
    
    if last_insertion_time_dt is None:
        # If the database is empty, insert the data directly
        add_data(cur, time_str, weight, operation)
        log_event(f"Weight data saved: {weight} grams, {operation}")
        return
    
    last_insertion_time = last_insertion_time_dt.timestamp()  # Convert to timestamp
    current_time = time.mktime(time.strptime(time_str, '%Y-%m-%d %H:%M:%S'))
    
    if current_time - last_insertion_time >= 10:
        add_data(cur, time_str, weight, operation)
        log_event(f"Weight data saved: {weight} grams, {operation}")
    else:
        log_event("Data not saved. Less than 10 seconds since the last insertion.")

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
                #Printing from SD
                octoprint_status = check_octoprint_status()
                print(f"OctoPrint status: {octoprint_status}")
                if octoprint_status and get_printer_status()["status"] != octoprint_status:
                    if (octoprint_status == "Printing" or octoprint_status == "Printing from SD"):
                        set_printer_status({"status": "Printing"})
                        log_event(f"OctoPrint status: {octoprint_status}")
                    else:
                        set_printer_status({"status": "Inactive"})
                        log_event("printer status set to Inactive")
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
        time.sleep(200)  # Check every few minutes

if __name__ == "__main__":
    threading.Thread(target=periodic_octoprint_check, daemon=True).start()
    threading.Thread(target=monitor_hardware, daemon=True).start()
    threading.Thread(target=update_camera_state, daemon=True).start()  # Start camera state update
    app.run(host="0.0.0.0", port=5001, debug=True)
