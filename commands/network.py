import re
import time
from core.filesystem import Directory, File
from commands.utils import resolve_path, _remove_quest_ips_from_intel # New import

def handle_nmap(game, args):
    if not args:
        game.console.history.append("  usage: nmap <ip_address>")
        return
    target_ip = args[0]
    if target_ip not in game.servers:
        game.console.history.append("  Host not found.")
        return
    
    game.console.history.append(f"  Scanning {target_ip}... Trace increased.")
    game.add_trace(0.15)
    target_server = game.servers[target_ip]
    
    if target_server.server_type == 'root':
        game.console.history.append("  VULNERABILITY DETECTED: Port 22 open with outdated SSH version. Encryption can be bypassed.")
        target_server.vulnerability_found = True
    else:
        game.console.history.append("  Scan complete. No obvious vulnerabilities found.")

def handle_ssh(game, args):
    if not args:
        game.console.history.append("  usage: ssh <user>@<ip_address>")
        return
    
    if len(args) == 1:
        match = re.match(r"(\w+)@([\d\.]+)", args[0])
        if not match:
            game.console.history.append("  usage: ssh <user>@<ip_address> or ssh <user> <ip_address>")
            return
        user, ip = match.groups()
    elif len(args) == 2:
        user = args[0]
        ip = args[1]
    else:
        game.console.history.append("  usage: ssh <user>@<ip_address> or ssh <user> <ip_address>")
        return
    if ip not in game.servers:
        game.console.history.append(f"  ssh: connect to host {ip} port 22: Connection refused")
        game.add_trace(0.05)
        return
        
    target_server = game.servers[ip]
    target_server.is_discovered = True
    
    if user not in target_server.accounts:
        game.console.history.append(f"  Permission denied (publickey,password).")
        game.add_trace(0.1)
        return

    if target_server.accounts.get(user) == 'guest' or not target_server.accounts.get(user):
        game.console.history.append(f"  Authentication successful. Welcome to {target_server.name}.")
        game.player.current_server = target_server
        game.player.current_directory = target_server.fs
        game.player.user = user
        return

    game.console.is_password_prompt = True
    def check_password(password):
        if target_server.accounts.get(user) == password:
            game.console.history.append(f"  Authentication successful. Welcome to {target_server.name}.")
            game.player.current_server = target_server
            game.player.current_directory = target_server.fs
            game.player.user = user
            
            # Update intel for the successfully connected IP
            # This logic needs to be updated for categorized intel
            # if target_server.ip in game.player.intel:
            #     game.player.intel[target_server.ip]["ip_seen"] = True
            # else:
            #     game.player.intel[target_server.ip] = {"desc": target_server.name, "user": None, "pass": None, "ip_seen": True, "user_seen": False, "pass_seen": False}

            # --- Quest Progress Tracking (new) ---
            for quest_id, quest_data in list(game.player.active_quests.items()):
                if quest_data["objective_type"] == "ssh_to_ip" and target_server.ip == quest_data["objective_target"]:
                    game.console.history.append(f"  [+] Quest '{quest_data['title']}' objective met: SSH to '{target_server.ip}'.")
                    game.player.completed_quests[quest_id] = quest_data
                    del game.player.active_quests[quest_id]
                    _remove_quest_ips_from_intel(game, quest_id)
                    if quest_data["reward_type"] == "creds":
                        game.player.software_currency += quest_data["reward_amount"]
                        game.console.history.append(f"  [+] {quest_data['reward_amount']} Creds added to wallet.")
                    elif quest_data["reward_type"] == "chips":
                        game.player.hardware_currency += quest_data["reward_amount"]
                        game.console.history.append(f"  [+] {quest_data['reward_amount']} Chips added to wallet.")
                    
                    # Award Street Cred
                    if "street_cred_reward" in quest_data:
                        game.player.street_cred += quest_data["street_cred_reward"]
                        game.console.history.append(f"  [+] {quest_data['street_cred_reward']} Street Cred gained!")
                    
                    # Generate and add a new quest
                    from commands.utils import _generate_and_add_new_quest # Import here to avoid circular dependency
                    _generate_and_add_new_quest(game, quest_id)
        else:
            game.console.history.append("  Permission denied, please try again.")
            game.add_trace(0.15)
    game.console.password_callback = check_password

def handle_grep(game, args):
    if len(args) < 2:
        game.console.history.append("  usage: grep <pattern> <file>")
        return
    pattern, file_path = args[0], args[1]
    target_file = resolve_path(game, file_path)
    if isinstance(target_file, File):
        matches = []
        for line in target_file.content.splitlines():
            if re.search(pattern, line, re.IGNORECASE):
                matches.append(f"  > {line}")
        if matches:
            game.console.history.extend(matches)
    else:
        game.console.history.append(f"  grep: {file_path}: No such file or directory")

def handle_tcpdump(game, args):
    capture_file = game.player.current_server.fs.get_child(".tcp_capture")
    if isinstance(capture_file, File):
        game.console.history.append(f"--- BEGINNING PACKET CAPTURE ON {game.player.current_server.name} ---")
        game.console.history.extend(f"  {line}" for line in capture_file.content.splitlines())
        game.console.history.append("--- END PACKET CAPTURE ---")
        game.add_trace(0.2)
    else:
        game.console.history.append("  tcpdump: no network traffic to capture on this interface.")

def handle_find(game, args):
    if not args:
        game.console.history.append("  usage: find <filename>")
        return
    
    filename_pattern = args[0]
    results = []
    # Simple find from the root of the current server
    def search_dir(directory, path):
        for name, item in directory.children.items():
            current_path = f"{path}/{name}"
            if re.search(filename_pattern, name, re.IGNORECASE):
                results.append(current_path)
            if isinstance(item, Directory):
                search_dir(item, current_path)
    
    search_dir(game.player.current_server.fs, '')
    if results:
        game.console.history.extend(results)
    else:
        game.console.history.append("  find: no matching files found.")

def handle_portscan(game, args):
    if not args:
        game.console.history.append("  usage: portscan <ip_address>")
        return
    target_ip = args[0]
    if target_ip not in game.servers:
        game.console.history.append("  Host not found.")
        return
    
    game.console.history.append(f"  Initiating deep scan on {target_ip}... Trace increased.")
    game.add_trace(0.25)
    target_server = game.servers[target_ip]

    # The generator will place a hidden file with port info
    port_info_file = target_server.fs.get_child(".ports")
    if isinstance(port_info_file, File):
        game.console.history.append("--- OPEN PORTS ---")
        game.console.history.extend(f"  {line}" for line in port_info_file.content.splitlines())
    else:
        game.console.history.append("  22/ssh") # Default

    if target_server.server_type == 'root':
        game.console.history.append("  VULNERABILITY DETECTED: Port 22 open with outdated SSH version. Encryption can be bypassed.")
        target_server.vulnerability_found = True
