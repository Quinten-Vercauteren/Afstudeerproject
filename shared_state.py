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
            return {"printer_status": {"status": "Inactive"}, "servicing": False}

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