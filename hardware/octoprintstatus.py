# Sources:
# ChatGPT model: OpenAI GPT-4 (03/12/2024)
# Requests library: https://docs.python-requests.org/en/latest/
# OctoPrint API: https://docs.octoprint.org/en/master/api/

import requests

# Configuratie
OCTOPRINT_URL = "http://octoproject.local/api/printer"
OCTOPRINT_API_KEY = "74E412EF48194068AC402721CDB6086F"

def check_octoprint_status():
    """Controleer de status van OctoPrint."""
    headers = {"X-Api-Key": OCTOPRINT_API_KEY}
    try:
        response = requests.get(OCTOPRINT_URL, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["state"]["text"]  # Bijv. "Printing", "Operational", etc.
    except requests.RequestException as e:
        print(f"[ERROR] OctoPrint niet bereikbaar: {e}")
        return None
    
print(check_octoprint_status())
