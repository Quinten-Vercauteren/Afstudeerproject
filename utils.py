# Sources:
# ChatGPT model: OpenAI GPT-4
# Python datetime module: https://docs.python.org/3/library/datetime.html

from datetime import datetime

def log_event(message):
    """Log een gebeurtenis met timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")
