# Documentation and sources:
# JSON module: https://docs.python.org/3/library/json.html
# Threading module: https://docs.python.org/3/library/threading.html
# File handling: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files
# ChatGPT model: OpenAI GPT-4 (2024) - https://chatgpt.com/

import json
import threading

state_lock = threading.Lock()
state_file = "/home/Octo/projectdir/Afstudeerproject/state.json"

def read_state():
    with state_lock:
        try:
            with open(state_file, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {"printer_status": {"status": "Inactive"}, "servicing": False, "last_known_status": "Unknown"}

def write_state(state):
    with state_lock:
        with open(state_file, 'w') as file:
            json.dump(state, file)

def get_printer_status():
    state = read_state()
    return state["printer_status"]

def set_printer_status(status):
    state = read_state()
    state["printer_status"] = status
    write_state(state)

def get_servicing_state():
    state = read_state()
    return state["servicing"]

def toggle_servicing_state():
    state = read_state()
    state["servicing"] = not state["servicing"]
    write_state(state)

def get_last_known_status():
    state = read_state()
    return state.get("last_known_status", "Unknown")

def set_last_known_status(status):
    state = read_state()
    state["last_known_status"] = status
    write_state(state)