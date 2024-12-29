import time
import sys
sys.path.insert(0, '/home/Octo/projectdir/Afstudeerproject/hx711py')
from hx711 import HX711
import RPi.GPIO as GPIO

GPIO.setwarnings(False)  # Suppress GPIO warnings

hx = None

def setup_hx711(data_pin=5, clock_pin=6, reference_unit=1933):
    global hx
    hx = HX711(data_pin, clock_pin)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(reference_unit)
    hx.reset()
    hx.tare()
    return hx

def reinit_hx711():
    global hx
    hx.reset()
    hx.tare()
    print("HX711 reinitialized and tared.")

def get_weight(hx, num_readings=5):
    try:
        weight = hx.get_weight(num_readings)
        hx.power_down()
        hx.power_up()
        return weight
    except Exception as e:
        print(f"Error reading weight: {e}")
        return None

def clean_and_exit():
    print("Cleaning...")
    GPIO.cleanup()
    print("Bye!")

def get_filament_weight():
    try:
        weight = get_weight(hx)
        if weight is not None:
            print(f"Current weight: {weight}")
            return weight
        else:
            print("Error reading weight")
            return None
    except (KeyboardInterrupt, SystemExit):
        clean_and_exit()
        return None

hx = setup_hx711()
time.sleep(1)
get_filament_weight()
