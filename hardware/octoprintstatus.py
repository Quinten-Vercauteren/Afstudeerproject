# Sources:
# ChatGPT model: OpenAI GPT-4 (03/12/2024)
# Requests library: https://docs.python-requests.org/en/latest/
# OctoPrint API: https://docs.octoprint.org/en/master/api/

import requests
import config

def check_octoprint_status():
    """Controleer de status van OctoPrint."""
    headers = {"X-Api-Key": config.OCTOPRINT_API_KEY}
    try:
        response = requests.get(config.OCTOPRINT_URL, headers=headers)
        response.raise_for_status()  # Raise an error for HTTP errors
        data = response.json()

        state = data.get("state")
        if state == "Printing":
            print("The printer is actively printing.")
            return state
        else:
            print(f"The printer is not printing. Current state: {state}")
            return state
    except requests.RequestException as e:
        print(f"[ERROR] OctoPrint niet bereikbaar: {e}")
        return None

print(check_octoprint_status())
