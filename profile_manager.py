import json
import os

PROFILE_PATH = "profile.json"

def get_default_profile():
    """Returns a new, default player profile."""
    return {
        "commands": ["ls", "cat", "cd", "ssh", "ping", "grep", "find"], # Added grep and find
        "software_currency": 0,
        "hardware_currency": 0,
        "hardware_inventory": [],
        "intel": {
            "127.0.0.1": {"desc": "Home PC", "user": None, "pass": None, "ip_seen": True, "user_seen": False, "pass_seen": False},
            "192.168.1.10": {"desc": "Chronosync Workstation", "user": None, "pass": None, "ip_seen": True, "user_seen": False, "pass_seen": False},
            "13.37.13.37": {"desc": "Black Market", "user": None, "pass": None, "ip_seen": True, "user_seen": False, "pass_seen": False}
        },
        "jobs_completed": {},
        "active_quests": {},
        "completed_quests": {},
        "street_cred": 0 # New currency
    }

def load_profile():
    """Loads the player profile, validating structure and types."""
    if not os.path.exists(PROFILE_PATH):
        return get_default_profile()
    
    try:
        with open(PROFILE_PATH, 'r') as f:
            loaded_data = json.load(f)
        
        default_data = get_default_profile()
        for key, default_value in default_data.items():
            if key not in loaded_data or type(loaded_data[key]) is not type(default_value):
                loaded_data[key] = default_value
        
        return loaded_data

    except (json.JSONDecodeError, IOError):
        return get_default_profile()

def save_profile(player):
    """Saves the player's current state to profile.json."""
    profile_data = {
        "commands": player.commands,
        "software_currency": player.software_currency,
        "hardware_currency": player.hardware_currency,
        "hardware_inventory": player.hardware_inventory,
        "intel": player.intel,
        "jobs_completed": player.jobs_completed,
        "active_quests": player.active_quests,
        "completed_quests": player.completed_quests,
        "street_cred": player.street_cred # Save street cred
    }
    with open(PROFILE_PATH, 'w') as f:
        json.dump(profile_data, f, indent=4)

def has_save_file():
    return os.path.exists(PROFILE_PATH)

def delete_profile():
    if os.path.exists(PROFILE_PATH):
        os.remove(PROFILE_PATH)
