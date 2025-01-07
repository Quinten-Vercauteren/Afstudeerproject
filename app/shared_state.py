import threading

# Shared state variables
servicing = False
printer_status = {"status": "Unknown"}

# Lock for thread-safe access
state_lock = threading.Lock()