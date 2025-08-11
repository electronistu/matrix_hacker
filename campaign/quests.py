# campaign/quests.py

# --- COMMAND TIERS (for difficulty scaling) ---
COMMAND_TIERS = {
    "easy": ["ls", "cat", "cd", "ping"],
    "medium": ["ssh", "grep", "find"],
    "hard": ["tcpdump", "portscan"]
}

# --- QUEST TEMPLATES (for dynamic generation) ---
QUEST_TEMPLATES = {
    "easy_ping_template": {
        "title": "Friends Favor: Ping Test",
        "description": "A friend needs you to ping a specific IP address to check connectivity. Use the 'ping' command. Target IP: {target_ip}",
        "objective_type": "ping_ip",
        "objective_target_placeholder": "dynamic_ip", # Placeholder for IP
        "reward_type": "creds",
        "reward_amount": 50,
        "street_cred_reward": 10,
        "street_cred_required": 0,
        "available_at_category": "home_missions", # Category for dynamic generation
        "required_commands": ["ping"]
    },
    "easy_read_file_template": {
        "title": "Data Retrieval: Basic Log",
        "description": "Locate a simple log file on a local server. The file is named: {target_file}. Read its content to find the key information, then deliver: {key_info}",
        "objective_type": "deliver_item",
        "objective_target_placeholder": "dynamic_keyword",
        "reward_type": "creds",
        "reward_amount": 75,
        "street_cred_reward": 15,
        "street_cred_required": 0,
        "available_at_category": "home_missions",
        "required_commands": ["cat"]
    },
    "medium_log_analysis_template": {
        "title": "Work Job: Log Analysis",
        "description": "Analyze a system log on a remote server ({target_ip}) and find the username of the last logged-in administrator. Log file: {target_file}. Deliver the username.",
        "objective_type": "deliver_item",
        "objective_target_placeholder": "dynamic_username",
        "reward_type": "creds",
        "reward_amount": 300,
        "street_cred_reward": 25,
        "street_cred_required": 0,
        "available_at_category": "work_missions",
        "required_commands": ["ssh", "grep"]
    },
    "medium_find_file_template": {
        "title": "Work Job: Locate Hidden Config",
        "description": "A critical configuration file is hidden on a remote server ({target_ip}). Find the file named '{target_file}' and extract its password.",
        "objective_type": "deliver_item",
        "objective_target_placeholder": "dynamic_password",
        "reward_type": "creds",
        "reward_amount": 350,
        "street_cred_reward": 30,
        "street_cred_required": 0,
        "available_at_category": "work_missions",
        "required_commands": ["ssh", "find"]
    },
    "hard_data_exfil_template": {
        "title": "Black Market: Data Exfiltration",
        "description": "Exfiltrate a highly sensitive data file from a heavily secured server ({target_ip}). File: {target_file}. Deliver the file content (or a hash of it).",
        "objective_type": "deliver_item",
        "objective_target_placeholder": "dynamic_hash",
        "reward_type": "chips",
        "reward_amount": 1000,
        "street_cred_reward": 50,
        "street_cred_required": 0,
        "available_at_category": "blackmarket_missions",
        "required_commands": ["ssh", "tcpdump"]
    },
    "hard_bounty_chimera_vault": { # Specific quest, not a generic template
        "title": "Bounty: Project Chimera Data Vault",
        "description": "Locate the IP address of 'Project Chimera's primary data vault. Deliver the IP to the black market server.",
        "objective_type": "deliver_item",
        "objective_target": "10.0.0.50", # Hardcoded target
        "reward_type": "chips",
        "reward_amount": 500,
        "street_cred_reward": 50,
        "street_cred_required": 75,
        "delivery_location": "black-market",
        "difficulty": "hard",
        "available_at_category": "blackmarket_missions",
        "required_commands": ["nmap", "portscan"] # Assuming these are needed to find the vault
    }
}

# This will be populated dynamically by the game
QUESTS = {}