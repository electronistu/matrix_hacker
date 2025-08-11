# campaign/quests.py

# --- COMMAND TIERS (for difficulty scaling) ---
COMMAND_TIERS = {
    "easy": ["ls", "cat", "cd", "ping"],
    "medium": ["ssh", "grep", "find"],
    "hard": ["tcpdump", "portscan", "nmap"]
}

# --- QUEST TEMPLATES (for dynamic generation) ---
QUEST_TEMPLATES = {
    # --- HOME MISSIONS (EASY) ---
    "home_easy_ping": {
        "title": "Friends Favor: Ping Test",
        "description": "A friend needs you to ping a specific IP address to check connectivity. Target IP: {target_ip}",
        "objective_type": "ping_ip",
        "target_type": "remote_ip_home_network", # New: Generate a 10.x.x.x IP
        "reward_type": "creds",
        "reward_amount": 50,
        "street_cred_reward": 10,
        "street_cred_required": 0,
        "available_at_category": "home_missions",
        "required_commands": ["ping"]
    },
    "home_easy_read_file": {
        "title": "Data Retrieval: Basic Log",
        "description": "Locate a simple log file on a remote server ({target_ip}). The file is named: {target_file}. Read its content to find the key information, then deliver: {key_info}",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_home_network", # New: Generate a 10.x.x.x IP
        "target_file_name": "report.txt", # New: Specific file name
        "reward_type": "creds",
        "reward_amount": 75,
        "street_cred_reward": 15,
        "street_cred_required": 0,
        "available_at_category": "home_missions",
        "required_commands": ["ssh", "cat"]
    },
    "home_easy_explore_dir": {
        "title": "Local Exploration: Directory Scan",
        "description": "Explore a specific directory on a remote server ({target_ip}) and report its contents. Target directory: {target_directory}. Deliver the name of any hidden file (starting with '.').",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_home_network", # New: Generate a 10.x.x.x IP
        "reward_type": "creds",
        "reward_amount": 60,
        "street_cred_reward": 12,
        "street_cred_required": 0,
        "available_at_category": "home_missions",
        "required_commands": ["ssh", "ls"]
    },
    "home_easy_find_file": {
        "title": "Local Search: Hidden File",
        "description": "Find a specific hidden file on a remote server ({target_ip}). File: {target_file}. Deliver its content.",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_home_network", # New: Generate a 10.x.x.x IP
        "reward_type": "creds",
        "reward_amount": 80,
        "street_cred_reward": 18,
        "street_cred_required": 0,
        "available_at_category": "home_missions",
        "required_commands": ["ssh", "find", "cat"]
    },

    # --- HOME MISSIONS (MEDIUM) ---
    "home_medium_ssh": {
        "title": "Network Access: Local Device",
        "description": "Access a local network device. IP: {target_ip}. Deliver the device's name.",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_home_network", # New: Generate a 10.x.x.x IP
        "reward_type": "creds",
        "reward_amount": 150,
        "street_cred_reward": 25,
        "street_cred_required": 10,
        "available_at_category": "home_missions",
        "required_commands": ["ssh"]
    },
    "home_medium_grep": {
        "title": "Log Analysis: Home Network",
        "description": "Analyze a log file on a local network device ({target_ip}) and find a specific entry: {keyword}. Deliver the entry.",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_home_network", # New: Generate a 10.x.x.x IP
        "target_file_name": "/var/log/system.log", # New: Specific file name
        "reward_type": "creds",
        "reward_amount": 180,
        "street_cred_reward": 28,
        "street_cred_required": 15,
        "available_at_category": "home_missions",
        "required_commands": ["ssh", "grep"]
    },

    # --- WORK MISSIONS (MEDIUM) ---
    "work_medium_log_analysis": {
        "title": "Work Job: Log Analysis",
        "description": "Analyze a system log on a remote server ({target_ip}) and find the username of the last logged-in administrator. Log file: {target_file}. Deliver the username.",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_work_network", # New: Generate a 192.168.1.x IP
        "target_file_name": "/var/log/auth.log", # New: Specific file name
        "reward_type": "creds",
        "reward_amount": 300,
        "street_cred_reward": 25,
        "street_cred_required": 0, # Available from start for work server
        "available_at_category": "work_missions",
        "required_commands": ["ssh", "grep"]
    },
    "work_medium_find_file": {
        "title": "Work Job: Locate Hidden Config",
        "description": "A critical configuration file is hidden on a remote server ({target_ip}). Find the file named '{target_file}' and extract its password.",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_work_network", # New: Generate a 192.168.1.x IP
        "reward_type": "creds",
        "reward_amount": 350,
        "street_cred_reward": 30,
        "street_cred_required": 0, # Available from start for work server
        "available_at_category": "work_missions",
        "required_commands": ["ssh", "find"]
    },
    "work_medium_portscan": {
        "title": "Network Recon: Work Server Ports",
        "description": "Perform a port scan on a work server ({target_ip}) and identify an open port. Deliver the port number.",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_work_network", # New: Generate a 192.168.1.x IP
        "reward_type": "creds",
        "reward_amount": 400,
        "street_cred_reward": 35,
        "street_cred_required": 30,
        "available_at_category": "work_missions",
        "required_commands": ["ssh", "portscan"]
    },

    # --- WORK MISSIONS (HARD) ---
    "work_hard_tcpdump": {
        "title": "Data Interception: Work Network",
        "description": "Intercept network traffic on a work server ({target_ip}) to capture sensitive data. Deliver the captured data.",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_work_network", # New: Generate a 192.168.1.x IP
        "reward_type": "chips",
        "reward_amount": 750,
        "street_cred_reward": 45,
        "street_cred_required": 40,
        "available_at_category": "work_missions",
        "required_commands": ["ssh", "tcpdump"]
    },

    # --- BLACK MARKET MISSIONS (HARD) ---
    "blackmarket_hard_data_exfil": {
        "title": "Black Market: Data Exfiltration",
        "description": "Exfiltrate a highly sensitive data file from a heavily secured server ({target_ip}). File: {target_file}. Deliver the file content (or a hash of it).",
        "objective_type": "deliver_item",
        "target_type": "remote_ip_blackmarket_network", # New: Generate a 13.37.x.x IP
        "reward_type": "chips",
        "reward_amount": 1000,
        "street_cred_reward": 50,
        "street_cred_required": 0, # Available from start for black market
        "available_at_category": "blackmarket_missions",
        "required_commands": ["ssh", "tcpdump"]
    },
    "blackmarket_hard_chimera_vault": {
        "title": "Bounty: Project Chimera Data Vault",
        "description": "Locate the IP address of 'Project Chimera's primary data vault. Deliver the IP to the black market server.",
        "objective_type": "deliver_item",
        "target_type": "specific_ip", # New: Hardcoded target
        "target_ip": "10.0.0.50", # Hardcoded target IP
        "reward_type": "chips",
        "reward_amount": 500,
        "street_cred_reward": 50,
        "street_cred_required": 75,
        "delivery_location": "black-market",
        "available_at_category": "blackmarket_missions",
        "required_commands": ["nmap", "portscan"]
    }
}

# This will be populated dynamically by the game
QUESTS = {}