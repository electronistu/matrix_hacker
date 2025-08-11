from core.commands import COMMAND_MAP
from core.market_commands import MARKET_COMMAND_MAP

class CommandExecutor:
    def __init__(self, game_instance):
        self.game = game_instance

    def execute_command(self, command_full):
        parts = command_full.split()
        if not parts:
            return
        command_name = parts[0]
        args = parts[1:]

        # Special handling for 'list quests' to ensure it always calls handle_list_quests
        if command_name == 'list' and args and args[0] == 'quests':
            from commands.quest import handle_list_quests
            handle_list_quests(self.game, args[1:]) # Pass remaining args after 'quests'
            return # Command handled, exit

        if self.game.player.current_server.server_type == "black_market":
            active_command_map = {**COMMAND_MAP, **MARKET_COMMAND_MAP}
            prompt_type = "-market"
        else:
            active_command_map = COMMAND_MAP
            prompt_type = "-bash"
        handler = active_command_map.get(command_name)
        if handler:
            if command_name in self.game.player.commands or command_name in ['list', 'buy', 'help', 'exit', 'cd', 'pwd', 'accept', 'deliver']:
                 handler(self.game, args)
            else:
                self.game.console.history.append(f"  {prompt_type}: command not found: {command_name}")
        else:
            self.game.console.history.append(f"  {prompt_type}: command not found: {command_name}")
        if self.game.game_active:
            self.game.game_loop.check_game_over_conditions() # Call through game_loop

    def add_trace(self, base_amount):
        modifier = 1.0
        if "ice_firewall_v1" in self.game.player.hardware_inventory:
            modifier -= 0.1
        self.game.system_trace += base_amount * modifier
