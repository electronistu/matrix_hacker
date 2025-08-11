from core.network import Server

class Player:
    def __init__(self, starting_server: Server, profile_data: dict):
        self.current_server = starting_server
        self.current_directory = starting_server.fs
        self.user = "operative"
        self.home_ip = "127.0.0.1"
        
        # Load from profile
        self.commands = profile_data["commands"]
        self.software_currency = profile_data["software_currency"]
        self.hardware_currency = profile_data["hardware_currency"]
        self.hardware_inventory = profile_data["hardware_inventory"]
        self.intel = {
            "known": profile_data["intel"], # Existing known IPs
            "home_missions": {},
            "work_missions": {},
            "blackmarket_missions": {}
        }
        self.jobs_completed = profile_data.get("jobs_completed", {})
        self.active_quests = profile_data.get("active_quests", {})
        self.completed_quests = profile_data.get("completed_quests", {})
        self.quest_ips = profile_data.get("quest_ips", {})
        self.street_cred = profile_data.get("street_cred", 0) # Initialize street_cred
