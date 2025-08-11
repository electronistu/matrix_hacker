import pygame as pg
import sys
import re
import random
import time

from settings import *
from core.filesystem import Directory, File
from core.network import Server
from ui.console import Console
from core.commands import COMMAND_MAP
from core.market_commands import MARKET_COMMAND_MAP
from campaign.generator import CampaignGenerator
import profile_manager

# Import moved components
from game_core.player import Player
from game_core.game_loop import GameLoop
from game_core.hud import HUD
from game_core.command_executor import CommandExecutor
from game_core.path_resolver import PathResolver


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font = pg.font.Font(pg.font.match_font('monospace'), 16)
        # self.scanline_surface = pg.Surface((512, HEIGHT)).convert_alpha() # Removed
        self.hud_surface = pg.Surface((WIDTH * INTEL_PANEL_WIDTH_RATIO, HEIGHT)) # Adjusted dimensions
        self.dynamic_quests = {}
        self.system_trace = 0.1 # Initialize system_trace here

        # Initialize moved components
        self.game_loop = GameLoop(self)
        self.hud = HUD(self)
        self.command_executor = CommandExecutor(self)
        self.path_resolver = PathResolver(self)

    def new_game(self, player_profile):
        # self.system_trace = 0.1 # Moved to __init__
        self.campaign_generator = CampaignGenerator(self) # Store as attribute
        self.servers, initial_intel, quest_ips_from_generator = self.campaign_generator.generate_campaign(num_missions=5)
        self.player = Player(self.servers["127.0.0.1"], player_profile)
        self.player.intel["known"].update(initial_intel)
        # Populate quest_ips from generator for main mission chain
        self.player.quest_ips.update(quest_ips_from_generator)
        self.console = Console(self)

        # Generate initial quests for each category
        from campaign.quest_generator import generate_dynamic_quest
        from campaign.quests import QUESTS # Import QUESTS to add generated quests

        # Home Quest
        home_quest = generate_dynamic_quest(
            game_instance=self,
            player_street_cred=self.player.street_cred,
            player_commands=self.player.commands
        )
        if home_quest:
            QUESTS[home_quest["id"]] = home_quest

        # Work Quest
        work_quest = generate_dynamic_quest(
            game_instance=self,
            player_street_cred=self.player.street_cred,
            player_commands=self.player.commands
        )
        if work_quest:
            QUESTS[work_quest["id"]] = work_quest

        # Black Market Quest (Bounty)
        # The bounty_chimera_vault is a specific hardcoded quest, not a template
        # We'll add it directly to QUESTS and create its file
        bounty_quest_id = "hard_bounty_chimera_vault"
        from campaign.quests import QUEST_TEMPLATES # Import QUEST_TEMPLATES to get the specific bounty quest
        if bounty_quest_id in QUEST_TEMPLATES:
            bounty_quest = QUEST_TEMPLATES[bounty_quest_id].copy()
            bounty_quest["id"] = bounty_quest_id
            QUESTS[bounty_quest_id] = bounty_quest
            # Add its IP to quest_ips if it's an IP-based objective
            if bounty_quest.get("objective_type") in ["ping_ip", "ssh_to_ip", "tcpdump_capture"] and re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', bounty_quest.get("objective_target", "")):
                if bounty_quest_id not in self.player.quest_ips:
                    self.player.quest_ips[bounty_quest_id] = []
                self.player.quest_ips[bounty_quest_id].append(bounty_quest["objective_target"])
                # Also add to intel panel immediately
                if bounty_quest.get("available_at_category") == "blackmarket_missions":
                    if bounty_quest["objective_target"] not in self.player.intel["known"]:
                        self.player.intel["blackmarket_missions"][bounty_quest["objective_target"]] = {
                            "desc": f"Quest Target ({bounty_quest['title']})",
                            "user": None, "pass": None,
                            "ip_seen": True, "user_seen": False, "pass_seen": False,
                            "category": "blackmarket_missions"
                        }
                        self.console.history.append(f"  [+] New mission IP discovered: {bounty_quest['objective_target']} (Category: blackmarket_missions)")

        # Black Market Quest (Dynamic)
        black_market_quest = generate_dynamic_quest(
            game_instance=self,
            player_street_cred=self.player.street_cred,
            player_commands=self.player.commands
        )
        if black_market_quest:
            QUESTS[black_market_quest["id"]] = black_market_quest
        self.console.history.extend([
            ">>> SECURE BOOT SEQUENCE COMPLETE...",
            "--- Welcome to your personal terminal, Operative. ---",
            "A new contract from Chronosync is waiting. Check 'chronosync_contract.txt'."
        ])
        self.game_loop.run_main_game_loop() # Delegate to GameLoop

    # Delegate methods to their respective classes
    def run_main_game_loop(self):
        self.game_loop.run_main_game_loop()

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND) # Clear the screen
        
        # Draw HUD (Intel Panel)
        self.hud.update_and_draw_hud()
        self.screen.blit(self.hud.hud_surface, (WIDTH * CONSOLE_WIDTH_RATIO, 0)) # Position on the right
        
        # Draw Console
        self.console.draw(self.screen, console_width=WIDTH * CONSOLE_WIDTH_RATIO) # Pass console_width
        
        pg.display.flip()

    def update_and_draw_hud(self):
        self.hud.update_and_draw_hud()

    def draw_trace_bar(self, surface):
        self.hud.draw_trace_bar(surface)

    def draw_text(self, surface, text, size, x, y, align="topleft", color=COLOR_TEXT):
        self.hud.draw_text(surface, text, size, x, y, align, color)

    def get_current_path(self):
        return self.path_resolver.get_current_path()

    def execute_command(self, command_full):
        self.command_executor.execute_command(command_full)

    def add_trace(self, base_amount):
        self.command_executor.add_trace(base_amount)

    def check_game_over_conditions(self):
        self.game_loop.check_game_over_conditions()

    def run_game_over_sequence(self):
        self.game_loop.run_game_over_sequence()

    def run_game_win_sequence(self):
        self.game_loop.run_game_win_sequence()