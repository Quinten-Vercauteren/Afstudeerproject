# Documentation and sources:
# ChatGPT model: OpenAI GPT-4 (03/12/2024)
# Python datetime module: https://docs.python.org/3/library/datetime.html

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def log_event(message):
    """Log an event with a timestamp."""
    logging.info(message)
