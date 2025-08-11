import re
from core.filesystem import Directory, File
from campaign.quests import QUESTS # This import will be needed by _remove_quest_ips_from_intel
from campaign.quest_generator import generate_dynamic_quest # New import

def resolve_path(game, path_str):
    if not path_str:
        return game.player.current_directory
    if path_str.startswith('~'):
        home_path = f"/home/{game.player.user}"
        path_str = path_str.replace('~', home_path, 1)
    
    current_node = game.player.current_directory
    if path_str.startswith('/'):
        current_node = game.player.current_server.fs
        path_parts = path_str.strip('/').split('/')
    else:
        path_parts = path_str.split('/')
    
    if path_parts == ['']:
        return current_node
        
    for i, part in enumerate(path_parts):
        if part == '..':
            if current_node.parent:
                current_node = current_node.parent
        elif part != '.' and part != '':
            next_node = current_node.get_child(part)
            if next_node:
                if i == len(path_parts) - 1:
                    return next_node
                elif isinstance(next_node, Directory):
                    current_node = next_node
                else:
                    return None # Path goes through a file
            else:
                return None
    return current_node

def _remove_quest_ips_from_intel(game, quest_id):
    if quest_id in game.player.quest_ips:
        quest_data = game.player.completed_quests.get(quest_id) or game.player.active_quests.get(quest_id)
        if quest_data:
            quest_category = quest_data.get("available_at_category")
            if quest_category == "home-pc":
                intel_category_key = "home_missions"
            elif quest_category == "work-serv":
                intel_category_key = "work_missions"
            elif quest_category == "black-market":
                intel_category_key = "blackmarket_missions"
            else:
                intel_category_key = None

            if intel_category_key and intel_category_key in game.player.intel:
                for ip in game.player.quest_ips[quest_id]:
                    if ip in game.player.intel[intel_category_key]:
                        del game.player.intel[intel_category_key][ip]
                        game.console.history.append(f"  [+] Removed {ip} from {intel_category_key} Intel panel (Quest {quest_id} completed).")
        del game.player.quest_ips[quest_id] # Remove the quest's IP list

def _generate_and_add_new_quest(game, completed_quest_id):
    """
    Generates a new quest based on the completed quest's category and player progress,
    and adds it to the game.
    """
    completed_quest_data = QUESTS.get(completed_quest_id)
    if not completed_quest_data:
        game.console.history.append(f"  Error: Completed quest {completed_quest_id} not found in QUESTS.")
        return

    quest_category = completed_quest_data.get("available_at_category") # Use available_at_category from template
    if not quest_category:
        game.console.history.append(f"  Error: Quest {completed_quest_id} has no 'available_at_category'.")
        return

    # Generate a new quest
    new_quest = generate_dynamic_quest(
        game_instance=game,
        player_street_cred=game.player.street_cred,
        player_commands=game.player.commands,
        quest_category=quest_category, # Generate quest for the same category
        last_quest_id=completed_quest_id # Pass the ID of the just completed quest
    )

    if new_quest:
        game.console.history.append(f"  [+] New quest '{new_quest['title']}' generated!")
        # Add a file to the appropriate jobs directory to notify the player
        jobs_dir_path = None
        if quest_category == "home_missions":
            jobs_dir_path = game.servers["127.0.0.1"].fs.get_child('home').get_child('operative').get_child('jobs')
        elif quest_category == "work_missions":
            jobs_dir_path = game.servers["192.168.1.10"].fs.get_child('home').get_child('jobs')
        elif quest_category == "blackmarket_missions":
            jobs_dir_path = game.servers["13.37.13.37"].fs.get_child('jobs')

        if jobs_dir_path:
            pass
        else:
            game.console.history.append(f"  Warning: Could not find jobs directory for category {quest_category}.")