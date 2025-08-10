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

class Player:
    def __init__(self, starting_server: Server, profile_data: dict):
        self.current_server = starting_server
        self.current_directory = starting_server.fs
        self.user = "operative"
        self.home_ip = "127.0.0.1"
        
        # Load from profile
        self.commands = profile_data["commands"]
        self.software_currency = profile_data["software_currency"]
        self.hardware_currency = profile_data["hardware_currency"]
        self.hardware_inventory = profile_data["hardware_inventory"]
        self.intel = profile_data["intel"]

class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font = pg.font.Font(pg.font.match_font('monospace'), 16)
        self.grid_offset = 0
        self.scanline_surface = pg.Surface((512, HEIGHT)).convert_alpha()
        self.hud_surface = pg.Surface((WIDTH * 0.4, HEIGHT))

    def new_game(self, player_profile):
        self.system_trace = 0.1
        generator = CampaignGenerator(self)
        self.servers = generator.generate_campaign(num_missions=5)
        self.player = Player(self.servers["127.0.0.1"], player_profile)
        self.console = Console(self)
        self.console.history.extend([
            ">>> SECURE BOOT SEQUENCE COMPLETE...",
            "--- Welcome to your personal terminal, Operative. ---",
            "A new contract from Chronosync is waiting. Check 'chronosync_contract.txt'."
        ])
        self.scanline_surface.fill((0, 0, 0, 0))
        for y in range(0, HEIGHT, 4):
            pg.draw.line(self.scanline_surface, (0, 0, 0, 30), (0, y), (512, y), 2)
        self.run_main_game_loop()

    def run_main_game_loop(self):
        self.game_active = True
        while self.game_active:
            self.dt = self.clock.tick(FPS) / 1000
            current_server = self.player.current_server
            if current_server.server_type == "work_server" or current_server.ip == self.player.home_ip:
                self.system_trace = max(0.1, self.system_trace - 0.001 * self.dt)
            elif current_server.server_type == "black_market":
                pass
            else:
                self.add_trace(0.002 * self.dt)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game_active = False
                    self.running = False
                self.console.handle_event(event)
            self.console.update(self.dt)
            self.draw()

    def draw(self):
        pg.draw.rect(self.screen, (0, 5, 0), (0, 0, WIDTH * 0.6, HEIGHT))
        self.update_and_draw_hud()
        self.screen.blit(self.hud_surface, (WIDTH * 0.6, 0))
        self.console.draw(self.screen)
        self.screen.blit(self.scanline_surface, (WIDTH * 0.6, 0))
        pg.display.flip()

    def update_and_draw_hud(self):
        self.hud_surface.fill(COLOR_BACKGROUND)
        map_area_x_start = 0 # Relative to the HUD surface
        self.grid_offset = (self.grid_offset + self.dt * 10) % 32
        for x in range(0, int(WIDTH * 0.4) + 32, 32):
            line_x = map_area_x_start + x - self.grid_offset
            pg.draw.line(self.hud_surface, COLOR_GRID, (line_x, 0), (line_x, HEIGHT))
        for y in range(0, HEIGHT + 32, 32):
            line_y = y - self.grid_offset
            pg.draw.line(self.hud_surface, COLOR_GRID, (map_area_x_start, line_y), (WIDTH * 0.4, line_y))
        
        self.draw_trace_bar(self.hud_surface)
        
        hud_x = WIDTH * 0.02
        y_pos = 80
        self.draw_text(self.hud_surface, "== HARDWARE ==", 18, hud_x, y_pos, align="topleft")
        y_pos += 30
        if self.player.hardware_inventory:
            for item in self.player.hardware_inventory:
                self.draw_text(self.hud_surface, f"- {item}", 16, hud_x, y_pos, align="topleft")
                y_pos += 20
        else:
            self.draw_text(self.hud_surface, "- Stock OS", 16, hud_x, y_pos, align="topleft")
            y_pos += 20
        y_pos += 20
        self.draw_text(self.hud_surface, "== INTEL ==", 18, hud_x, y_pos, align="topleft")
        y_pos += 30
        if self.player.intel:
            for ip, data in self.player.intel.items():
                desc = data.get("desc", "Unknown")
                user = data.get("user", "???")
                password = data.get("pass", "???")
                self.draw_text(self.hud_surface, f"- {ip:<15} ({desc})", 16, hud_x, y_pos, align="topleft")
                y_pos += 20
                self.draw_text(self.hud_surface, f"    user: {user} | pass: {password}", 14, hud_x, y_pos, align="topleft")
                y_pos += 20
        else:
            self.draw_text(self.hud_surface, "- No new targets", 16, hud_x, y_pos, align="topleft")
            y_pos += 20
        y_pos += 20
        self.draw_text(self.hud_surface, "== WALLET ==", 18, hud_x, y_pos, align="topleft")
        y_pos += 30
        self.draw_text(self.hud_surface, f"Creds: {self.player.software_currency}c", 16, hud_x, y_pos, align="topleft")
        y_pos += 20
        self.draw_text(self.hud_surface, f"Chips: {self.player.hardware_currency}h", 16, hud_x, y_pos, align="topleft")

    def draw_trace_bar(self, surface):
        map_area_x = WIDTH * 0.02
        trace_percent_raw = self.system_trace
        trace_percent_display = int(trace_percent_raw * 100)
        trace_percent_clamped = max(0.0, min(1.0, trace_percent_raw))
        r = int(min(255, 255 * (trace_percent_clamped * 2)))
        g = int(min(255, 510 * (1 - trace_percent_clamped)))
        b = 0
        trace_color = (r, g, b)
        trace_text = f"SYSTEM TRACE: {trace_percent_display}%"
        self.draw_text(surface, trace_text, 18, map_area_x, 20, align="topleft")
        pg.draw.rect(surface, (50,50,50), (map_area_x, 45, (WIDTH * 0.4) - 40, 20))
        pg.draw.rect(surface, trace_color, (map_area_x, 45, ((WIDTH * 0.4) - 40) * trace_percent_clamped, 20))

    def draw_text(self, surface, text, size, x, y, align="topleft"):
        font = pg.font.Font(None, size)
        text_surface = font.render(text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect()
        if align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "center":
            text_rect.center = (x,y)
        surface.blit(text_surface, text_rect)

    def get_current_path(self):
        path = []
        current = self.player.current_directory
        while current:
            path.append(current.name)
            current = current.parent
        if len(path) <= 1: return "/"
        else: return "/" + "/".join(reversed(path[:-1]))

    def execute_command(self, command_full):
        parts = command_full.split()
        if not parts:
            return
        command_name = parts[0]
        args = parts[1:]
        if self.player.current_server.server_type == "black_market":
            active_command_map = {**COMMAND_MAP, **MARKET_COMMAND_MAP}
            prompt_type = "-market"
        else:
            active_command_map = COMMAND_MAP
            prompt_type = "-bash"
        handler = active_command_map.get(command_name)
        if handler:
            if command_name in self.player.commands or command_name in ['list', 'buy', 'help', 'exit', 'cd', 'pwd']:
                 handler(self, args)
            else:
                self.console.history.append(f"  {prompt_type}: command not found: {command_name}")
        else:
            self.console.history.append(f"  {prompt_type}: command not found: {command_name}")
        if self.game_active:
            self.check_game_over_conditions()

    def add_trace(self, base_amount):
        modifier = 1.0
        if "ice_firewall_v1" in self.player.hardware_inventory:
            modifier -= 0.1
        self.system_trace += base_amount * modifier

    def check_game_over_conditions(self):
        if self.system_trace >= 1.0:
            self.run_game_over_sequence()

    def run_game_over_sequence(self):
        self.game_active = False
        self.screen.fill((0, 0, 0))
        font = pg.font.Font(pg.font.match_font('monospace'), 48)
        text_surface = font.render("CONNECTION TERMINATED", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        for i in range(255):
            self.screen.fill((0,0,0))
            text_surface.set_alpha(i)
            self.screen.blit(text_surface, text_rect)
            pg.display.flip()
            pg.time.wait(5)
        pg.time.wait(1000)
        for _ in range(15):
            flicker_surface = self.screen.copy()
            flicker_surface.fill((0,0,0))
            text_surface.set_alpha(random.randint(50, 200))
            flicker_surface.blit(text_surface, text_rect)
            self.screen.blit(flicker_surface, (0,0))
            pg.display.flip()
            pg.time.wait(random.randint(50, 150))
        text_surface.set_alpha(255)
        self.screen.blit(text_surface, text_rect)
        pg.display.flip()
        pg.time.wait(2000)
        self.running = False

    def run_game_win_sequence(self):
        self.game_active = False
        self.screen.fill((0, 10, 0))
        font = pg.font.Font(pg.font.match_font('monospace'), 48)
        text_surface = font.render("OBJECTIVE COMPLETE", True, (0, 255, 70))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40))
        font_small = pg.font.Font(pg.font.match_font('monospace'), 24)
        sub_text_surface = font_small.render("The Genesis Echo is complete.", True, (0, 255, 70))
        sub_text_rect = sub_text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20))
        for i in range(255):
            self.screen.fill((0, 10, 0))
            text_surface.set_alpha(i)
            sub_text_surface.set_alpha(i)
            self.screen.blit(text_surface, text_rect)
            self.screen.blit(sub_text_surface, sub_text_rect)
            pg.display.flip()
            pg.time.wait(10)
        pg.time.wait(4000)
        self.running = False