# Bronnen:
# https://pypi.org/project/hx711/
'''
import RPi.GPIO as GPIO
from hx711 import HX711
import time

# Raw data corresponding to the known weight (1274 grams)
known_weight_raw_data = [
    32259.6, 32230.6, 32235.2, 32242.6, 32240, 32231,
    32228, 32226.8, 32220.4, 32201
]

# Step 1: Calculate the average raw value of the known weight
mean_known_weight = sum(known_weight_raw_data) / len(known_weight_raw_data)
print(f"Mean raw value for known weight: {mean_known_weight}")

# Known weight in grams
known_weight = 1274  # in grams

# Step 2: Calculate the scale ratio
scale_ratio = mean_known_weight / known_weight
print(f"Calculated scale ratio: {scale_ratio:.6f}")

# Initialize HX711
hx711 = HX711(
        dout_pin=5,
        pd_sck_pin=6,
        channel='A',
        gain=64
    )
hx711.reset()  # Reset the HX711 (optional but recommended)

# Step 3: Measure and display weight in grams (with try-except block)
print("Starting measurements. Press Ctrl+C to stop.")
try:
    while True:
        # Get the raw data as a list
        raw_data = hx711.get_raw_data()  
        
        # Ensure the raw_data is not empty and is a list
        if isinstance(raw_data, list) and raw_data:
            # Calculate the mean of the raw data
            mean_raw_value = sum(raw_data) / len(raw_data)
            print(f"Mean raw value: {mean_raw_value}")

            # Convert the mean raw value to grams
            weight = mean_raw_value / scale_ratio  # Convert the raw value to grams using scale ratio
            print(f"Weight: {weight:.2f} grams")
        else:
            print("Error: Invalid raw data.")

except KeyboardInterrupt:
    print("Measurement stopped by user.")

finally:
    GPIO.cleanup()  # Always clean up GPIO in your scripts!
'''


import random
import time

# Initialize the weight of the spool (in grams)
weight = 1000

# Define the rate of filament usage per "printing cycle" (in grams)
min_usage = 5  # Minimum grams used per cycle
max_usage = 15  # Maximum grams used per cycle

print("Starting filament consumption simulation...\n")
while True:
    print(f"Current spool weight: {weight:.2f} grams")
    
    # Simulate a random amount of filament used
    filament_used = random.uniform(min_usage, max_usage)
    
    # Decrease the weight
    weight -= filament_used
    
    # Check if the spool weight drops below 200 grams
    if weight < 200:
        print("The spool is low on filament. Resetting to a full spool...")
        weight = 1000  # Reset to full spool
    
    # Wait for a short period to simulate time passing
    time.sleep(10)
