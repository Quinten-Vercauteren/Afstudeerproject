# Bronnen:
# https://pypi.org/project/hx711/

import RPi.GPIO as GPIO
from hx711 import HX711
import time
try:
    hx711 = HX711(
        dout_pin=5,
        pd_sck_pin=6,
        channel='A',
        gain=64
    )

    hx711.reset() # Before we start, reset the HX711 (not obligate)

    print ("starting measurements. Press Ctrl+C to stop")
    while True:
        raw_data = hx711.get_raw_data()
        print(raw_data)

        if isinstance(raw_data, list) and raw_data:
            average_value = sum(raw_data) / len(raw_data)
            print (f"Average reading: {average_value}")
        else:
            print ("Unexpected data format:", raw_data)

        time.sleep(1)

except KeyboardInterrupt:
    print ("Measurement stopped by user.")

finally:
    GPIO.cleanup()  # always do a GPIO cleanup in your scripts!
