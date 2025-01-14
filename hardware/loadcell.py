# Documentation Links:
# HX711: https://github.com/tatobari/hx711py

import time
import sys
sys.path.insert(0, '/home/Octo/projectdir/Afstudeerproject/hx711py')
from hx711 import HX711
import RPi.GPIO as GPIO

GPIO.setwarnings(False)  # Suppress GPIO warnings

hx = None

# Define the GPIO pin for the red LED
RED_LED_PIN = 17

def setup_hx711(data_pin=5, clock_pin=6, reference_unit=1497):
    """Initialize the HX711 sensor."""
    global hx
    hx = HX711(data_pin, clock_pin)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(reference_unit)
    hx.reset()
    hx.tare()
    return hx

def setup_gpio():
    """Setup GPIO pins."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(RED_LED_PIN, GPIO.OUT)
    GPIO.output(RED_LED_PIN, GPIO.LOW)

def reinit_hx711():
    """Reinitialize and tare the HX711 sensor."""
    global hx
    hx.reset()
    hx.tare()
    print("HX711 reinitialized and tared.")

def get_weight(hx, num_readings=5):
    """Get the weight from the HX711 sensor."""
    try:
        weight = hx.get_weight(num_readings)
        hx.power_down()
        hx.power_up()
        return weight
    except Exception as e:
        print(f"Error reading weight: {e}")
        return None

def clean_and_exit():
    """Clean up GPIO and exit."""
    print("Cleaning...")
    GPIO.cleanup()
    print("Bye!")

def get_filament_weight():
    """Get the current weight of the filament."""
    try:
        weight = get_weight(hx)
        print(weight)
        if weight is not None:
            if weight < 300:
                GPIO.output(RED_LED_PIN, GPIO.HIGH)  # Turn on the red LED
            else:
                GPIO.output(RED_LED_PIN, GPIO.LOW)   # Turn off the red LED
            return weight
        else:
            print("Error reading weight")
            return None
    except (KeyboardInterrupt, SystemExit):
        clean_and_exit()
        return None

# Initialize the HX711 sensor and GPIO on startup
hx = setup_hx711()
setup_gpio()
time.sleep(1)
