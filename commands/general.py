import re
import time
from core.filesystem import Directory, File
from commands.utils import resolve_path, _remove_quest_ips_from_intel # New import

from commands.utils import resolve_path, _remove_quest_ips_from_intel

HELP_MESSAGES = {
    "help": "  Usage: help [command]\n  Provides help for commands.",
    "pwd": "  Usage: pwd\n  Prints the current working directory.",
    "ls": "  Usage: ls [path]\n  Lists contents of directory.",
    "dir": "  Usage: dir [path]\n  Alias for ls.",
    "cd": "  Usage: cd <directory>\n  Changes current directory.",
    "cat": "  Usage: cat <file>\n  Displays file content.",
    "ssh": "  Usage: ssh <user>@<ip>\n  Connects to remote server.",
    "ping": "  Usage: ping <ip_address>\n  Sends network requests to a host.",
    "exit": "  Usage: exit\n  Exits the game.",
    "grep": "  Usage: grep <pattern> <file>\n  Searches for a pattern in a file.",
    "tcpdump": "  Usage: tcpdump\n  Captures network traffic.",
    "find": "  Usage: find <filename>\n  Searches for a file.",
    "portscan": "  Usage: portscan <ip_address>\n  Scans a host for open ports.",
    "deliver": "  Usage: deliver <keyword_or_item>\n  Delivers a quest objective. For 'find and deliver' quests, use the keyword found in the file.",
    "list": "  Usage: list quests | software | hardware\n  Lists available quests, software, or hardware.",
    "accept": "  Usage: accept <quest_id>\n  Accepts a quest.",
    "buy": "  Usage: buy <item_name>\n  Purchases an item from the market."
}

def handle_help(game, args):
    # HELP_MESSAGES is defined in this file, no need to import from core.commands
    if args:
        command_name = args[0].lower()
        if command_name in HELP_MESSAGES:
            game.console.history.append(HELP_MESSAGES[command_name])
        else:
            game.console.history.append(f"  No help entry for command: '{command_name}'")
    else:
        game.console.history.append(f'  Commands: {" ".join(sorted(game.player.commands))}')

def handle_pwd(game, args):
    game.console.history.append(game.get_current_path())

def handle_ls(game, args):
    path = args[0] if args else "."
    target_dir = resolve_path(game, path)
    if isinstance(target_dir, Directory):
        game.console.history.append("  ".join(target_dir.children.keys()) or "  (empty)")
    elif target_dir is None:
        game.console.history.append(f"  ls: cannot access '{path}': No such file or directory")
    else:
        game.console.history.append(path.split('/')[-1])

def handle_cd(game, args):
    if not args:
        path = '~'
    else:
        path = args[0]
    target_dir = resolve_path(game, path)
    if isinstance(target_dir, Directory):
        game.player.current_directory = target_dir
    else:
        game.console.history.append(f"  cd: no such directory: {path}")

def handle_cat(game, args):
    if not args:
        game.console.history.append("  usage: cat <file>")
        return
    path = args[0]
    target_file = resolve_path(game, path)
    if isinstance(target_file, File):
        filename = path.split('/')[-1]
        content = target_file.content
        
        game.console.history.extend([
            f"  --- Contents of {filename} ---",
            content,
            "  -------------------------"
        ])

        # --- Handle special file logic ---
        if filename.endswith(".hlp"):
            command_name = filename.split('.')[0]
            if command_name not in game.player.commands:
                game.player.commands.append(command_name)
                game.console.history.append(f"  [+] New command learned: {command_name}")
        
        elif filename == 'FINAL_entry.txt':
            game.run_game_win_sequence()

        # --- Quest Progress Tracking ---
        for quest_id, quest_data in list(game.player.active_quests.items()):
            if quest_data["objective_type"] == "read_file" and filename == quest_data["objective_target"]:
                game.console.history.append(f"  [+] Quest '{quest_data['title']}' objective met: Read '{filename}'.")
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

            elif quest_data["objective_type"] == "find_keyword" and quest_data["objective_target"].lower() in content.lower():
                game.console.history.append(f"  [+] Quest '{quest_data['title']}' objective met: Found keyword '{quest_data['objective_target']}'.")
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

        # --- Parse for Intel and Currency ---
        # Only award currency if the file is not a quest description
        if filename not in ["bounty_target.txt", "job1.txt"]:
            creds_match = re.search(r'(\d+)\s+Creds', content)
            if creds_match:
                amount = int(creds_match.group(1))
                game.player.software_currency += amount
                game.console.history.append(f"  [+] {amount} Creds added to wallet.")
            
            chips_match = re.search(r'(\d+)\s+Chips', content)
            if chips_match:
                amount = int(chips_match.group(1))
                game.player.hardware_currency += amount
                game.console.history.append(f"  [+] {amount} Chips added to wallet.")

        # Find the primary IP this file is about
        primary_ip = None
        ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', content)
        if ip_match:
            primary_ip = ip_match.group(1)
            # Only add to intel if it's not already a known IP
            if primary_ip not in game.player.intel["known"]:
                # This logic needs to be refined with the new intel structure
                pass # IP discovery will be handled by quest acceptance or specific actions
            
            # Mark IP as seen (this logic needs to be updated for categorized intel)
            # This part will be removed or heavily modified once intel is fully categorized
            # if primary_ip in game.player.intel:
            #     game.player.intel[primary_ip]["ip_seen"] = True

        # If we have a primary IP, look for other details to associate with it
        # This section also needs to be updated for categorized intel
        # if primary_ip:
        #     desc_match = re.search(r'\(Description:\s*(.*?)\)', content)
        #     if desc_match:
        #         game.player.intel[primary_ip]["desc"] = desc_match.group(1)

        #     credentials_match = re.search(r'(?:credentials\s+)?(\w+):(\S+)', content, re.IGNORECASE)
        #     if credentials_match:
        #         found_user = credentials_match.group(1)
        #         found_pass = credentials_match.group(2)

        #         if not game.player.intel[primary_ip]["user_seen"]:
        #             game.player.intel[primary_ip]["user"] = found_user
        #             game.player.intel[primary_ip]["user_seen"] = True
                
        #         if not game.player.intel[primary_ip]["pass_seen"]:
        #             game.player.intel[primary_ip]["pass"] = found_pass
        #             game.player.intel[primary_ip]["pass_seen"] = True
            
        #     if not game.player.intel[primary_ip]["user_seen"]:
        #         user_match = re.search(r'user:\s*(\w+)', content, re.IGNORECASE)
        #         if user_match:
        #             game.player.intel[primary_ip]["user"] = user_match.group(1)
        #             game.player.intel[primary_ip]["user_seen"] = True

        #     if not game.player.intel[primary_ip]["pass_seen"]:
        #         pass_match = re.search(r'pass:\s*(\S+)', content, re.IGNORECASE)
        #         if pass_match:
        #             game.player.intel[primary_ip]["pass"] = pass_match.group(1)
        #             game.player.intel[primary_ip]["pass_seen"] = True

    else:
        game.console.history.append(f"  cat: cannot access '{path}': No such file or directory")

def handle_exit(game, args):
    game.game_active = False
