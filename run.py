# Sources:
# ChatGPT model: GPT-4 by OpenAI (03/12/2024)
# Flask documentation: https://flask.palletsprojects.com/
# OctoPrint API documentation: https://docs.octoprint.org/en/master/api/printer.html

from app import create_app
from hardware import start_camera, detect_motion, get_filament_weight, check_octoprint_status
from utils import log_event
import threading
import time

app = create_app()

def monitor_hardware():
    """Monitor the printer hardware and track status."""
    log_event("Hardware monitoring started.")
    cap = None

    try:
        while True:
            status = check_octoprint_status()
            if status:
                log_event(f"OctoPrint status: {status}")
                if status.lower() == "printing":
                    log_event("Printer started!")
                    weight = get_filament_weight()
                    log_event(f"Filament weight at start: {weight} grams")
                elif status.lower() == "operational":
                    log_event("Printer stopped!")
                    weight = get_filament_weight()
                    log_event(f"Filament weight at stop: {weight} grams")
                time.sleep(5)
            else:
                if cap is None:
                    cap = start_camera()
                ret, frame1 = cap.read()
                time.sleep(0.1)
                ret, frame2 = cap.read()

                if detect_motion(frame1, frame2):
                    log_event("Motion detected (printer started).")
                    weight = get_filament_weight()
                    log_event(f"Filament weight at start: {weight} grams")
                else:
                    log_event("No motion detected (printer stopped).")
                time.sleep(5)

    except KeyboardInterrupt:
        log_event("Hardware monitoring stopped by user.")
    finally:
        if cap:
            cap.release()

if __name__ == "__main__":
    threading.Thread(target=monitor_hardware, daemon=True).start()
    app.run(host="0.0.0.0", port=5001, debug=True)
