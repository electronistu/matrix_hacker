import re
import time
from campaign.quests import QUESTS
from commands.utils import resolve_path, _remove_quest_ips_from_intel, _generate_and_add_new_quest # Added _generate_and_add_new_quest

def handle_deliver(game, args):
    if not args:
        game.console.history.append("  usage: deliver <item>")
        return

    delivered_item = " ".join(args) # Join all arguments to form the delivered item
    
    # Iterate through active quests to find a matching delivery
    quest_completed = False
    for quest_id, quest_data in list(game.player.active_quests.items()): # Use list() to allow modification during iteration
        if quest_data["objective_type"] == "deliver_item":
            # Check if delivery location matches current server/directory
            delivery_match = False
            if quest_data["delivery_location"] == "work-serv/jobs" and \
               game.player.current_server.name == "work-serv" and \
               game.player.current_directory.name == "jobs":
                delivery_match = True
            elif quest_data["delivery_location"] == "black-market" and \
                 game.player.current_server.name == "black-market":
                delivery_match = True
            elif quest_data["delivery_location"] == "home-pc" and \
                 game.player.current_server.name == "home-pc":
                delivery_match = True

            if delivery_match and delivered_item.lower() == quest_data["objective_target"].lower():
                # Quest completed!
                game.console.history.append(f"  Quest '{quest_data['title']}' complete!")
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
                _generate_and_add_new_quest(game, quest_id)
                
                game.player.completed_quests[quest_id] = quest_data # Move to completed
                del game.player.active_quests[quest_id] # Remove from active
                _remove_quest_ips_from_intel(game, quest_id)
                quest_completed = True
                break # Only complete one quest per delivery for now

    if not quest_completed:
        game.console.history.append(f"  No active quest matches delivery: '{delivered_item}'.")


def handle_list_quests(game, args):
    game.console.history.append("--- Available Quests ---")
    found_available = False
    current_server_name = game.player.current_server.name

    # Map server names to quest categories for filtering
    server_category_map = {
        "home-pc": "home_missions",
        "work-serv": "work_missions",
        "black-market": "blackmarket_missions"
    }
    current_server_category = server_category_map.get(current_server_name)

    if current_server_category:
        for quest_id, quest_data in QUESTS.items():
            quest_category = quest_data.get("available_at_category")

            if quest_id not in game.player.active_quests and quest_id not in game.player.completed_quests:
                # Check if the quest's category matches the current server's category
                if quest_category == current_server_category:
                    # Check Street Cred requirement
                    required_cred = quest_data.get("street_cred_required", 0)
                    if game.player.street_cred >= required_cred:
                        game.console.history.append(f"  [{quest_id}] {quest_data['title']}")
                        game.console.history.append(f"    Description: {quest_data['description']}")
                        game.console.history.append(f"    Reward: {quest_data['reward_amount']} {quest_data['reward_type']}")
                        game.console.history.append(f"    Requires: {required_cred} SC")
                        found_available = True
    if not found_available:
        game.console.history.append("  No new quests available at this time.")
    game.console.history.append("--- Active Quests ---")
    if game.player.active_quests:
        for quest_id, quest_data in game.player.active_quests.items():
            game.console.history.append(f"  [{quest_id}] {quest_data['title']} (Active)")
            game.console.history.append(f"    Description: {quest_data['description']}") # Display description instead of objective
            game.console.history.append(f"    Deliver to: {quest_data['delivery_location']}")
    else:
        game.console.history.append("  No active quests.")

def handle_accept_quest(game, args):
    if not args:
        game.console.history.append("  usage: accept <quest_id>") # Corrected usage message
        return
    
    quest_id = args[0]
    if quest_id in QUESTS:
        if quest_id in game.player.active_quests:
            game.console.history.append(f"  Quest '{quest_id}' is already active.")
        elif quest_id in game.player.completed_quests:
            game.console.history.append(f"  Quest '{quest_id}' has already been completed.")
        else:
            # Check Street Cred requirement
            required_cred = QUESTS[quest_id].get("street_cred_required", 0)
            if game.player.street_cred < required_cred:
                game.console.history.append(f"  Insufficient Street Cred. Requires {required_cred} SC.")
                return

            game.player.active_quests[quest_id] = QUESTS[quest_id]
            game.console.history.append(f"  Quest '{QUESTS[quest_id]['title']}' accepted! Check 'list quests' for details.")

            # Add quest IPs to the appropriate intel category
            quest_intel_category = QUESTS[quest_id].get("available_at_category") # Use available_at_category
            
            # Ensure quest_ips is populated for this quest
            if quest_id not in game.player.quest_ips:
                game.player.quest_ips[quest_id] = []
            
            # If the objective is IP-based, add it to quest_ips
            if "objective_type" in QUESTS[quest_id] and "objective_target" in QUESTS[quest_id]:
                obj_type = QUESTS[quest_id]["objective_type"]
                obj_target = QUESTS[quest_id]["objective_target"]
                # Corrected regex string: added closing single quote and dollar sign for end of string match
                if obj_type in ["ping_ip", "ssh_to_ip", "tcpdump_capture"] and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', obj_target):
                    game.player.quest_ips[quest_id].append(obj_target)
                    # Also add to intel panel immediately
                    if quest_intel_category and obj_target not in game.player.intel["known"]:
                        game.player.intel[quest_intel_category][obj_target] = {
                            "desc": f"Quest Target ({QUESTS[quest_id]['title']})",
                            "user": None, "pass": None,
                            "ip_seen": True, "user_seen": False, "pass_seen": False,
                            "category": quest_intel_category # Store category in intel entry
                        }
                        game.console.history.append(f"  [+] New mission IP discovered: {obj_target} (Category: {quest_intel_category})\n") # Added newline for better formatting
    else:
        game.console.history.append(f"  Quest '{quest_id}' not found.")

def handle_ping(game, args):
    if not args:
        game.console.history.append("  usage: ping <ip_address>")
        return
    target_ip = args[0]
    if target_ip not in game.servers:
        game.console.history.append("  Host not found.")
        game.add_trace(0.05)
        return
    
    game.console.history.append(f"  Pinging {target_ip}...")
    game.add_trace(0.1) # Small trace increase for ping

    # --- Quest Progress Tracking (new) ---
    for quest_id, quest_data in list(game.player.active_quests.items()):
        if quest_data["objective_type"] == "ping_ip" and target_ip == quest_data["objective_target"]:
            game.console.history.append(f"  [+] Quest '{quest_data['title']}' objective met: Pinged '{target_ip}'.")
            game.player.completed_quests[quest_id] = quest_data
            del game.player.active_quests[quest_id]
            _remove_quest_ips_from_intel(game, quest_id)
            # Award reward immediately for 'ping_ip' quests
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
            _generate_and_add_new_quest(game, quest_id)
            break # Assume only one quest per ping target for now

    game.console.history.append(f"  Reply from {target_ip}: bytes=32 time=10ms TTL=64")