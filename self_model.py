import json
import os

CORE_FILE = "core_memory.json"

def load_core():
    if not os.path.exists(CORE_FILE):
        return {}
    with open(CORE_FILE, "r") as f:
        return json.load(f)

def get_identity():
    core = load_core()
    return core.get("identity", "megabox")

def get_core_values():
    core = load_core()
    return core.get("core_values", [])

def get_personality_traits():
    core = load_core()
    return core.get("personality_traits", {})
