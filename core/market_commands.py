# core/market_commands.py

SOFTWARE_CATALOG = {
    "grep": 100,
    "nmap": 250,
    "tcpdump": 500,
    "find": 300,
    "portscan": 750,
}

HARDWARE_CATALOG = {
    "ice_firewall_v1": 1000,
    "stealth_router_v1": 2500,
    "trace_scrambler_v1": 5000,
}

def handle_list(game, args):
    if not args:
        game.console.history.append("  usage: list <software|hardware>")
        return
    
    category = args[0]
    if category == "software":
        game.console.history.append("--- Available Software (Creds) ---")
        for item, price in SOFTWARE_CATALOG.items():
            if item not in game.player.commands:
                game.console.history.append(f"  {item:<15} - {price}c")
    elif category == "hardware":
        game.console.history.append("--- Available Hardware (Chips) ---")
        for item, price in HARDWARE_CATALOG.items():
            if item not in game.player.hardware_inventory:
                game.console.history.append(f"  {item:<15} - {price}h")
    else:
        game.console.history.append(f"  Unknown category: {category}")

def handle_buy(game, args):
    if not args:
        game.console.history.append("  usage: buy <item_name>")
        return
        
    item_name = args[0]
    if item_name in SOFTWARE_CATALOG and item_name not in game.player.commands:
        price = SOFTWARE_CATALOG[item_name]
        if game.player.software_currency >= price:
            game.player.software_currency -= price
            game.player.commands.append(item_name)
            game.console.history.append(f"  Successfully purchased '{item_name}'.")
        else:
            game.console.history.append("  Error: Insufficient Creds.")
    elif item_name in HARDWARE_CATALOG and item_name not in game.player.hardware_inventory:
        price = HARDWARE_CATALOG[item_name]
        if game.player.hardware_currency >= price:
            game.player.hardware_currency -= price
            game.player.hardware_inventory.append(item_name)
            game.console.history.append(f"  Successfully purchased '{item_name}'.")
        else:
            game.console.history.append("  Error: Insufficient Chips.")
    else:
        game.console.history.append(f"  Unknown or already owned item: {item_name}")

MARKET_COMMAND_MAP = {
    'list': handle_list,
    'buy': handle_buy,
    # 'exit' command will be handled by the main command handler
}
