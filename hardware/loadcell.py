# Bronnen:
# https://pypi.org/project/hx711/
'''
# Sources:
# ChatGPT model: OpenAI GPT-4 (03/12/2024)
# HX711 Python library: https://github.com/tatobari/hx711py

from hx711 import HX711

# Configuratie voor HX711
HX711_DOUT = 5  # Data-uitgang
HX711_SCK = 6   # Clock signaal

def get_filament_weight():
    """Meet het huidige filamentgewicht."""
    hx = HX711(dout=HX711_DOUT, pd_sck=HX711_SCK)
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(1)  # Pas aan voor jouw sensor
    hx.reset()
    hx.tare()
    weight = hx.get_weight(5)  # Gemiddelde van 5 metingen
    hx.power_down()
    hx.power_up()
    return weight
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
