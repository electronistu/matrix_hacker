import random
from campaign.quests import QUEST_TEMPLATES, COMMAND_TIERS, QUESTS # Import QUESTS to add generated quests
from core.filesystem import File, Directory
from core.network import Server

def generate_dynamic_quest(game_instance, player_street_cred, player_commands, last_quest_id=None):
    """
    Generates a dynamic quest based on player's street cred and learned commands.
    """
    available_templates = []
    
    eligible_categories = []
    if player_street_cred < 20: # Example threshold for easy quests
        eligible_categories.append("home_missions")
    if player_street_cred >= 15: # Example threshold for medium quests
        eligible_categories.append("work_missions")
    if player_street_cred >= 40: # Example threshold for hard quests
        eligible_categories.append("blackmarket_missions")

    # Filter templates based on street cred, required commands, and eligible categories
    for template_id, template_data in QUEST_TEMPLATES.items():
        if template_data.get("street_cred_required", 0) <= player_street_cred:
            commands_met = True
            for cmd in template_data.get("required_commands", []):
                if cmd not in player_commands:
                    commands_met = False
                    break
            if commands_met:
                if template_data.get("available_at_category") in eligible_categories:
                    available_templates.append(template_id)

    

    if not available_templates:
        return None

    # Try to avoid picking the same quest template as the last completed one
    if last_quest_id and len(available_templates) > 1:
        last_completed_quest_data = QUESTS.get(last_quest_id)
        if last_completed_quest_data and "template_id" in last_completed_quest_data:
            last_template_id = last_completed_quest_data["template_id"]
            if last_template_id in available_templates:
                temp_available_templates = [t for t in available_templates if t != last_template_id]
                if temp_available_templates:
                    available_templates = temp_available_templates

    # If there are still multiple available templates, try to pick a more interesting one
    if len(available_templates) > 1:
        # Prioritize quests that require commands from higher tiers that the player has
        prioritized_templates = []
        for tier_name in ["hard", "medium", "easy"]: # Iterate from hard to easy
            for cmd in COMMAND_TIERS.get(tier_name, []):
                if cmd in player_commands:
                    for template_id in available_templates:
                        template_data = QUEST_TEMPLATES[template_id]
                        if cmd in template_data.get("required_commands", []) and template_id not in prioritized_templates:
                            prioritized_templates.append(template_id)
            
            if prioritized_templates:
                available_templates = prioritized_templates
        
    chosen_template_id = random.choice(available_templates)
    chosen_template = QUEST_TEMPLATES[chosen_template_id]

    # Instantiate the quest from the template
    quest_id = f"dynamic_quest_{len(QUESTS) + 1}_{random.randint(1000, 9999)}" # Unique ID
    
    # Deep copy to avoid modifying the template
    new_quest = chosen_template.copy()
    new_quest["id"] = quest_id
    new_quest["template_id"] = chosen_template_id
    
    # Generate dynamic content based on objective type
    generated_ips = [] # To track IPs generated for this quest
    if new_quest["objective_type"] == "ping_ip":
        target_ip = f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
        new_quest["objective_target"] = target_ip
        new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
        
        # Create a simple server for the ping target
        ping_server = game_instance.campaign_generator._create_server(target_ip, f"ping-target-{quest_id}", server_type="default")
        game_instance.servers[target_ip] = ping_server
        generated_ips.append(target_ip)

    elif new_quest["objective_type"] == "deliver_item":
        if new_quest.get("objective_target_placeholder") == "dynamic_keyword":
            # For easy_read_file_template
            target_file = "report.txt"
            key_info = random.choice(["project alpha", "phase two", "secure data", "classified"])
            new_quest["objective_target"] = key_info
            new_quest["description"] = new_quest["description"].format(target_file=target_file, key_info=key_info)

            # Place the file on the home server's operative directory
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            home_operative_dir.add_child(File(target_file, f"Log entry: KEY_INFO: {key_info}. End of report. Deliver this keyword."))
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc for easy read file

        elif new_quest.get("objective_target_placeholder") == "dynamic_username":
            # For medium_log_analysis_template
            target_ip = f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            target_file = "/var/log/auth.log"
            admin_user = random.choice(["sysadmin", "root", "network_admin"])
            admin_pass = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
            new_quest["objective_target"] = admin_user
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, target_file=target_file)

            # Create a server with the log file and credentials
            log_server = game_instance.campaign_generator._create_server(target_ip, f"log-server-{quest_id}", server_type="default")
            log_server.add_user("guest", "guest")
            log_server.add_user(admin_user, admin_pass)
            log_server.fs.get_child('var').add_child(Directory('log'))
            log_server.fs.get_child('var').get_child('log').add_child(File("auth.log", f"INFO: User 'guest' logged in.\nERROR: Failed login for user 'admin'.\nINFO: User '{admin_user}' logged in from 192.168.1.5.\n"))
            game_instance.servers[target_ip] = log_server
            generated_ips.append(target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_password":
            # For medium_find_file_template
            target_ip = f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            target_file = random.choice(["config.bak", "secret.conf", "backup.ini"])
            hidden_pass = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=10))
            new_quest["objective_target"] = hidden_pass
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, target_file=target_file)

            # Create a server with hidden file
            find_server = game_instance.campaign_generator._create_server(target_ip, f"find-server-{quest_id}", server_type="default")
            find_server.add_user("guest", "guest")
            dummy_dirs = [find_server.fs.get_child('home')]
            for _ in range(5): # Create some dummy directories
                d = Directory(f"dir_{random.randint(100,999)}")
                random.choice(dummy_dirs).add_child(d)
                dummy_dirs.append(d)
            random.choice(dummy_dirs).add_child(File(target_file, f"password={hidden_pass}"))
            game_instance.servers[target_ip] = find_server
            generated_ips.append(target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_hash":
            # For hard_data_exfil_template
            target_ip = f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}"
            target_file = random.choice(["secret_data.enc", "top_secret.bin", "project_x.dat"])
            data_hash = ''.join(random.choices('abcdef0123456789', k=32)) # MD5-like hash
            new_quest["objective_target"] = data_hash
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, target_file=target_file)

            # Create a server with the sensitive file
            exfil_server = game_instance.campaign_generator._create_server(target_ip, f"exfil-server-{quest_id}", server_type="default")
            exfil_server.add_user("admin", "password123") # Example credentials
            exfil_server.fs.add_child(File(target_file, f"DATA_HASH:{data_hash}"))
            game_instance.servers[target_ip] = exfil_server
            generated_ips.append(target_ip)
            new_quest["delivery_location"] = "black-market" # Deliver to black market

        elif new_quest.get("objective_target_placeholder") == "dynamic_hidden_file":
            # For easy_explore_dir_template
            target_directory_name = random.choice(["temp", "logs", "data", "archive"])
            hidden_file_name = f".{random.choice(['config', 'cache', 'secret'])}.{random.randint(100, 999)}.txt"
            
            # Create the target directory and hidden file on the home PC
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            target_directory = Directory(target_directory_name)
            home_operative_dir.add_child(target_directory)
            target_directory.add_child(File(hidden_file_name, f"Hidden content for {hidden_file_name}."))
            
            new_quest["objective_target"] = hidden_file_name # The name of the hidden file is the objective
            new_quest["description"] = new_quest["description"].format(target_directory=target_directory_name)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_file_content":
            # For easy_find_file_home_template
            target_file_name = random.choice(["notes.txt", "todo.txt", "important.log"])
            file_content = f"This is the content of {target_file_name}. The secret is: {random.choice(['alpha', 'beta', 'gamma'])}."
            
            # Create the file on the home PC
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            home_operative_dir.add_child(File(target_file_name, file_content))
            
            new_quest["objective_target"] = file_content # Deliver the content
            new_quest["description"] = new_quest["description"].format(target_file=target_file_name)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_device_name":
            # For medium_ssh_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            device_name = random.choice(["router", "printer", "nas", "camera"])
            
            # Create a simple server for the device
            device_server = game_instance.campaign_generator._create_server(target_ip, device_name, server_type="device")
            device_server.add_user("admin", "password") # Simple credentials
            game_instance.servers[target_ip] = device_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = device_name # Deliver the device name
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_log_entry":
            # For medium_grep_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            log_file = "/var/log/system.log"
            keyword = random.choice(["ERROR", "WARNING", "CRITICAL"])
            log_entry = f"[{keyword}] User 'guest' failed login from {random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}."
            
            # Create a server with the log file
            log_server = game_instance.campaign_generator._create_server(target_ip, "log-server", server_type="log")
            log_server.add_user("user", "pass")
            log_server.fs.get_child('var').add_child(Directory('log'))
            log_server.fs.get_child('var').get_child('log').add_child(File("system.log", log_entry))
            game_instance.servers[target_ip] = log_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = log_entry # Deliver the log entry
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, keyword=keyword)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_port_number":
            # For medium_portscan_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            open_port = random.choice([21, 23, 80, 443, 8080])
            
            # Create a server with the open port info
            port_server = game_instance.campaign_generator._create_server(target_ip, "work-device", server_type="work_device")
            port_server.fs.add_child(File(".ports", f"Open ports: {open_port}, 22, 23"))
            game_instance.servers[target_ip] = port_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = str(open_port) # Deliver the port number as string
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_captured_data":
            # For hard_tcpdump_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            captured_data = f"Sensitive data: {random.choice(['financial_report', 'project_x_specs', 'employee_records'])} - {random.randint(1000, 9999)}"
            
            # Create a server with the captured data
            capture_server = game_instance.campaign_generator._create_server(target_ip, "work-hub", server_type="work_hub")
            capture_server.fs.add_child(File(".tcp_capture", f"Packet capture: {captured_data}"))
            game_instance.servers[target_ip] = capture_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = captured_data # Deliver the captured data
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_file_content":
            # For easy_find_file_home_template
            target_file_name = random.choice(["notes.txt", "todo.txt", "important.log"])
            file_content = f"This is the content of {target_file_name}. The secret is: {random.choice(['alpha', 'beta', 'gamma'])}."
            
            # Create the file on the home PC
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            home_operative_dir.add_child(File(target_file_name, file_content))
            
            new_quest["objective_target"] = file_content # Deliver the content
            new_quest["description"] = new_quest["description"].format(target_file=target_file_name)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_device_name":
            # For medium_ssh_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            device_name = random.choice(["router", "printer", "nas", "camera"])
            
            # Create a simple server for the device
            device_server = game_instance.campaign_generator._create_server(target_ip, device_name, server_type="device")
            device_server.add_user("admin", "password") # Simple credentials
            game_instance.servers[target_ip] = device_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = device_name # Deliver the device name
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_log_entry":
            # For medium_grep_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            log_file = "/var/log/system.log"
            keyword = random.choice(["ERROR", "WARNING", "CRITICAL"])
            log_entry = f"[{keyword}] User 'guest' failed login from {random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}."
            
            # Create a server with the log file
            log_server = game_instance.campaign_generator._create_server(target_ip, "log-server", server_type="log")
            log_server.add_user("user", "pass")
            log_server.fs.get_child('var').add_child(Directory('log'))
            log_server.fs.get_child('var').get_child('log').add_child(File("system.log", log_entry))
            game_instance.servers[target_ip] = log_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = log_entry # Deliver the log entry
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, keyword=keyword)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_port_number":
            # For medium_portscan_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            open_port = random.choice([21, 23, 80, 443, 8080])
            
            # Create a server with the open port info
            port_server = game_instance.campaign_generator._create_server(target_ip, "work-device", server_type="work_device")
            port_server.fs.add_child(File(".ports", f"Open ports: {open_port}, 22, 23"))
            game_instance.servers[target_ip] = port_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = str(open_port) # Deliver the port number as string
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_captured_data":
            # For hard_tcpdump_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            captured_data = f"Sensitive data: {random.choice(['financial_report', 'project_x_specs', 'employee_records'])} - {random.randint(1000, 9999)}"
            
            # Create a server with the captured data
            capture_server = game_instance.campaign_generator._create_server(target_ip, "work-hub", server_type="work_hub")
            capture_server.fs.add_child(File(".tcp_capture", f"Packet capture: {captured_data}"))
            game_instance.servers[target_ip] = capture_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = captured_data # Deliver the captured data
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_file_content":
            # For easy_find_file_home_template
            target_file_name = random.choice(["notes.txt", "todo.txt", "important.log"])
            file_content = f"This is the content of {target_file_name}. The secret is: {random.choice(['alpha', 'beta', 'gamma'])}."
            
            # Create the file on the home PC
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            home_operative_dir.add_child(File(target_file_name, file_content))
            
            new_quest["objective_target"] = file_content # Deliver the content
            new_quest["description"] = new_quest["description"].format(target_file=target_file_name)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_device_name":
            # For medium_ssh_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            device_name = random.choice(["router", "printer", "nas", "camera"])
            
            # Create a simple server for the device
            device_server = game_instance.campaign_generator._create_server(target_ip, device_name, server_type="device")
            device_server.add_user("admin", "password") # Simple credentials
            game_instance.servers[target_ip] = device_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = device_name # Deliver the device name
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_log_entry":
            # For medium_grep_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            log_file = "/var/log/system.log"
            keyword = random.choice(["ERROR", "WARNING", "CRITICAL"])
            log_entry = f"[{keyword}] User 'guest' failed login from {random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}."
            
            # Create a server with the log file
            log_server = game_instance.campaign_generator._create_server(target_ip, "log-server", server_type="log")
            log_server.add_user("user", "pass")
            log_server.fs.get_child('var').add_child(Directory('log'))
            log_server.fs.get_child('var').get_child('log').add_child(File("system.log", log_entry))
            game_instance.servers[target_ip] = log_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = log_entry # Deliver the log entry
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, keyword=keyword)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_port_number":
            # For medium_portscan_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            open_port = random.choice([21, 23, 80, 443, 8080])
            
            # Create a server with the open port info
            port_server = game_instance.campaign_generator._create_server(target_ip, "work-device", server_type="work_device")
            port_server.fs.add_child(File(".ports", f"Open ports: {open_port}, 22, 23"))
            game_instance.servers[target_ip] = port_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = str(open_port) # Deliver the port number as string
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_captured_data":
            # For hard_tcpdump_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            captured_data = f"Sensitive data: {random.choice(['financial_report', 'project_x_specs', 'employee_records'])} - {random.randint(1000, 9999)}"
            
            # Create a server with the captured data
            capture_server = game_instance.campaign_generator._create_server(target_ip, "work-hub", server_type="work_hub")
            capture_server.fs.add_child(File(".tcp_capture", f"Packet capture: {captured_data}"))
            game_instance.servers[target_ip] = capture_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = captured_data # Deliver the captured data
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_file_content":
            # For easy_find_file_home_template
            target_file_name = random.choice(["notes.txt", "todo.txt", "important.log"])
            file_content = f"This is the content of {target_file_name}. The secret is: {random.choice(['alpha', 'beta', 'gamma'])}."
            
            # Create the file on the home PC
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            home_operative_dir.add_child(File(target_file_name, file_content))
            
            new_quest["objective_target"] = file_content # Deliver the content
            new_quest["description"] = new_quest["description"].format(target_file=target_file_name)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_device_name":
            # For medium_ssh_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            device_name = random.choice(["router", "printer", "nas", "camera"])
            
            # Create a simple server for the device
            device_server = game_instance.campaign_generator._create_server(target_ip, device_name, server_type="device")
            device_server.add_user("admin", "password") # Simple credentials
            game_instance.servers[target_ip] = device_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = device_name # Deliver the device name
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_log_entry":
            # For medium_grep_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            log_file = "/var/log/system.log"
            keyword = random.choice(["ERROR", "WARNING", "CRITICAL"])
            log_entry = f"[{keyword}] User 'guest' failed login from {random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}."
            
            # Create a server with the log file
            log_server = game_instance.campaign_generator._create_server(target_ip, "log-server", server_type="log")
            log_server.add_user("user", "pass")
            log_server.fs.get_child('var').add_child(Directory('log'))
            log_server.fs.get_child('var').get_child('log').add_child(File("system.log", log_entry))
            game_instance.servers[target_ip] = log_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = log_entry # Deliver the log entry
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, keyword=keyword)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_port_number":
            # For medium_portscan_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            open_port = random.choice([21, 23, 80, 443, 8080])
            
            # Create a server with the open port info
            port_server = game_instance.campaign_generator._create_server(target_ip, "work-device", server_type="work_device")
            port_server.fs.add_child(File(".ports", f"Open ports: {open_port}, 22, 23"))
            game_instance.servers[target_ip] = port_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = str(open_port) # Deliver the port number as string
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_captured_data":
            # For hard_tcpdump_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            captured_data = f"Sensitive data: {random.choice(['financial_report', 'project_x_specs', 'employee_records'])} - {random.randint(1000, 9999)}"
            
            # Create a server with the captured data
            capture_server = game_instance.campaign_generator._create_server(target_ip, "work-hub", server_type="work_hub")
            capture_server.fs.add_child(File(".tcp_capture", f"Packet capture: {captured_data}"))
            game_instance.servers[target_ip] = capture_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = captured_data # Deliver the captured data
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_file_content":
            # For easy_find_file_home_template
            target_file_name = random.choice(["notes.txt", "todo.txt", "important.log"])
            file_content = f"This is the content of {target_file_name}. The secret is: {random.choice(['alpha', 'beta', 'gamma'])}."
            
            # Create the file on the home PC
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            home_operative_dir.add_child(File(target_file_name, file_content))
            
            new_quest["objective_target"] = file_content # Deliver the content
            new_quest["description"] = new_quest["description"].format(target_file=target_file_name)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_device_name":
            # For medium_ssh_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            device_name = random.choice(["router", "printer", "nas", "camera"])
            
            # Create a simple server for the device
            device_server = game_instance.campaign_generator._create_server(target_ip, device_name, server_type="device")
            device_server.add_user("admin", "password") # Simple credentials
            game_instance.servers[target_ip] = device_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = device_name # Deliver the device name
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_log_entry":
            # For medium_grep_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            log_file = "/var/log/system.log"
            keyword = random.choice(["ERROR", "WARNING", "CRITICAL"])
            log_entry = f"[{keyword}] User 'guest' failed login from {random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}."
            
            # Create a server with the log file
            log_server = game_instance.campaign_generator._create_server(target_ip, "log-server", server_type="log")
            log_server.add_user("user", "pass")
            log_server.fs.get_child('var').add_child(Directory('log'))
            log_server.fs.get_child('var').get_child('log').add_child(File("system.log", log_entry))
            game_instance.servers[target_ip] = log_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = log_entry # Deliver the log entry
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, keyword=keyword)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_port_number":
            # For medium_portscan_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            open_port = random.choice([21, 23, 80, 443, 8080])
            
            # Create a server with the open port info
            port_server = game_instance.campaign_generator._create_server(target_ip, "work-device", server_type="work_device")
            port_server.fs.add_child(File(".ports", f"Open ports: {open_port}, 22, 23"))
            game_instance.servers[target_ip] = port_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = str(open_port) # Deliver the port number as string
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_captured_data":
            # For hard_tcpdump_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            captured_data = f"Sensitive data: {random.choice(['financial_report', 'project_x_specs', 'employee_records'])} - {random.randint(1000, 9999)}"
            
            # Create a server with the captured data
            capture_server = game_instance.campaign_generator._create_server(target_ip, "work-hub", server_type="work_hub")
            capture_server.fs.add_child(File(".tcp_capture", f"Packet capture: {captured_data}"))
            game_instance.servers[target_ip] = capture_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = captured_data # Deliver the captured data
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_file_content":
            # For easy_find_file_home_template
            target_file_name = random.choice(["notes.txt", "todo.txt", "important.log"])
            file_content = f"This is the content of {target_file_name}. The secret is: {random.choice(['alpha', 'beta', 'gamma'])}."
            
            # Create the file on the home PC
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            home_operative_dir.add_child(File(target_file_name, file_content))
            
            new_quest["objective_target"] = file_content # Deliver the content
            new_quest["description"] = new_quest["description"].format(target_file=target_file_name)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_device_name":
            # For medium_ssh_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            device_name = random.choice(["router", "printer", "nas", "camera"])
            
            # Create a simple server for the device
            device_server = game_instance.campaign_generator._create_server(target_ip, device_name, server_type="device")
            device_server.add_user("admin", "password") # Simple credentials
            game_instance.servers[target_ip] = device_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = device_name # Deliver the device name
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_log_entry":
            # For medium_grep_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            log_file = "/var/log/system.log"
            keyword = random.choice(["ERROR", "WARNING", "CRITICAL"])
            log_entry = f"[{keyword}] User 'guest' failed login from {random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}."
            
            # Create a server with the log file
            log_server = game_instance.campaign_generator._create_server(target_ip, "log-server", server_type="log")
            log_server.add_user("user", "pass")
            log_server.fs.get_child('var').add_child(Directory('log'))
            log_server.fs.get_child('var').get_child('log').add_child(File("system.log", log_entry))
            game_instance.servers[target_ip] = log_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = log_entry # Deliver the log entry
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, keyword=keyword)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_port_number":
            # For medium_portscan_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            open_port = random.choice([21, 23, 80, 443, 8080])
            
            # Create a server with the open port info
            port_server = game_instance.campaign_generator._create_server(target_ip, "work-device", server_type="work_device")
            port_server.fs.add_child(File(".ports", f"Open ports: {open_port}, 22, 23"))
            game_instance.servers[target_ip] = port_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = str(open_port) # Deliver the port number as string
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_captured_data":
            # For hard_tcpdump_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            captured_data = f"Sensitive data: {random.choice(['financial_report', 'project_x_specs', 'employee_records'])} - {random.randint(1000, 9999)}"
            
            # Create a server with the captured data
            capture_server = game_instance.campaign_generator._create_server(target_ip, "work-hub", server_type="work_hub")
            capture_server.fs.add_child(File(".tcp_capture", f"Packet capture: {captured_data}"))
            game_instance.servers[target_ip] = capture_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = captured_data # Deliver the captured data
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_file_content":
            # For easy_find_file_home_template
            target_file_name = random.choice(["notes.txt", "todo.txt", "important.log"])
            file_content = f"This is the content of {target_file_name}. The secret is: {random.choice(['alpha', 'beta', 'gamma'])}."
            
            # Create the file on the home PC
            home_operative_dir = game_instance.servers["127.0.0.1"].fs.get_child('home').get_child('operative')
            home_operative_dir.add_child(File(target_file_name, file_content))
            
            new_quest["objective_target"] = file_content # Deliver the content
            new_quest["description"] = new_quest["description"].format(target_file=target_file_name)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_device_name":
            # For medium_ssh_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            device_name = random.choice(["router", "printer", "nas", "camera"])
            
            # Create a simple server for the device
            device_server = game_instance.campaign_generator._create_server(target_ip, device_name, server_type="device")
            device_server.add_user("admin", "password") # Simple credentials
            game_instance.servers[target_ip] = device_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = device_name # Deliver the device name
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_log_entry":
            # For medium_grep_home_template
            target_ip = f"10.0.0.{random.randint(2, 254)}" # Local network IP
            log_file = "/var/log/system.log"
            keyword = random.choice(["ERROR", "WARNING", "CRITICAL"])
            log_entry = f"[{keyword}] User 'guest' failed login from {random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}."
            
            # Create a server with the log file
            log_server = game_instance.campaign_generator._create_server(target_ip, "log-server", server_type="log")
            log_server.add_user("user", "pass")
            log_server.fs.get_child('var').add_child(Directory('log'))
            log_server.fs.get_child('var').get_child('log').add_child(File("system.log", log_entry))
            game_instance.servers[target_ip] = log_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = log_entry # Deliver the log entry
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip, keyword=keyword)
            new_quest["delivery_location"] = "home-pc" # Deliver to home-pc

        elif new_quest.get("objective_target_placeholder") == "dynamic_port_number":
            # For medium_portscan_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            open_port = random.choice([21, 23, 80, 443, 8080])
            
            # Create a server with the open port info
            port_server = game_instance.campaign_generator._create_server(target_ip, "work-device", server_type="work_device")
            port_server.fs.add_child(File(".ports", f"Open ports: {open_port}, 22, 23"))
            game_instance.servers[target_ip] = port_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = str(open_port) # Deliver the port number as string
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

        elif new_quest.get("objective_target_placeholder") == "dynamic_captured_data":
            # For hard_tcpdump_work_template
            target_ip = f"192.168.1.{random.randint(11, 254)}" # Work network IP
            captured_data = f"Sensitive data: {random.choice(['financial_report', 'project_x_specs', 'employee_records'])} - {random.randint(1000, 9999)}"
            
            # Create a server with the captured data
            capture_server = game_instance.campaign_generator._create_server(target_ip, "work-hub", server_type="work_hub")
            capture_server.fs.add_child(File(".tcp_capture", f"Packet capture: {captured_data}"))
            game_instance.servers[target_ip] = capture_server
            generated_ips.append(target_ip)
            
            new_quest["objective_target"] = captured_data # Deliver the captured data
            new_quest["description"] = new_quest["description"].format(target_ip=target_ip)
            new_quest["delivery_location"] = "work-serv/jobs" # Deliver to work server jobs

    # Add generated IPs to game.player.quest_ips
    game_instance.player.quest_ips[quest_id] = generated_ips
    
    QUESTS[quest_id] = new_quest # Add to the global QUESTS dictionary
    return new_quest