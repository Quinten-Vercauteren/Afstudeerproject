import time
import sys
sys.path.insert(0, '/home/Octo/projectdir/Afstudeerproject/hx711py')
from hx711 import HX711
import RPi.GPIO as GPIO

def setup_hx711(data_pin=5, clock_pin=6, reference_unit=1624):
    hx = HX711(data_pin, clock_pin)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(reference_unit)
    hx.reset()
    return hx

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
        hx = setup_hx711()
        weight = get_weight(hx)
        if weight is not None:
            print(f"Current weight: {weight}")
        else:
            print("Error reading weight")
    except (KeyboardInterrupt, SystemExit):
        clean_and_exit()