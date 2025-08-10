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
from campaign.generator import CampaignGenerator

class Player:
    def __init__(self, starting_server: Server):
        self.current_server = starting_server
        self.current_directory = starting_server.fs
        self.user = "operative"
        self.commands = ["help", "ls", "dir", "cat", "cd", "pwd"]

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

    def new_game(self):
        self.system_trace = 0.1
        
        # The campaign generator creates the entire game world
        generator = CampaignGenerator(self)
        self.servers = generator.generate_campaign(num_missions=5)

        self.player = Player(self.servers["127.0.0.1"])
        self.console = Console(self)
        self.console.history.extend([
            ">>> SECURE CONNECTION ESTABLISHED...",
            "Control: Operative, you're in. Your first mission brief is in 'mission_1.txt'.",
            "Control: Use 'ls' to see files, and 'cat <filename>' to read them."
        ])
        self.scanline_surface.fill((0, 0, 0, 0))
        for y in range(0, HEIGHT, 4):
            pg.draw.line(self.scanline_surface, (0, 0, 0, 30), (0, y), (512, y), 2)

        self.run_main_game_loop()

    

    def run_main_game_loop(self):
        self.game_active = True
        while self.game_active:
            self.dt = self.clock.tick(FPS) / 1000
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game_active = False
                    self.running = False
                self.console.handle_event(event)
            self.console.update(self.dt)
            self.draw()

    def draw(self):
        self.screen.fill(COLOR_BACKGROUND)
        self.draw_background_grid()
        self.draw_network_map()
        self.draw_trace_bar()
        self.console.draw(self.screen)
        self.screen.blit(self.scanline_surface, (768, 0))
        pg.display.flip()

    def draw_background_grid(self):
        map_area_x_start = WIDTH * 0.6
        pg.draw.rect(self.screen, (0, 5, 0), (0, 0, map_area_x_start, HEIGHT))
        self.grid_offset = (self.grid_offset + self.dt * 10) % 32
        for x in range(0, int(WIDTH * 0.4) + 32, 32):
            line_x = map_area_x_start + x - self.grid_offset
            pg.draw.line(self.screen, COLOR_GRID, (line_x, 0), (line_x, HEIGHT))
        for y in range(0, HEIGHT + 32, 32):
            line_y = y - self.grid_offset
            pg.draw.line(self.screen, COLOR_GRID, (map_area_x_start, line_y), (WIDTH, line_y))

    def draw_network_map(self):
        for server in self.servers.values():
            if server.is_discovered:
                if server.ip != self.player.current_server.ip:
                    pg.draw.line(self.screen, COLOR_GRID, self.player.current_server.position, server.position, 1)
                color = COLOR_NODE_DEFAULT
                if server.server_type == 'root': color = COLOR_NODE_ROOT
                elif server.server_type == 'firewall': color = COLOR_NODE_FIREWALL
                pg.draw.rect(self.screen, color, (server.position[0] - 15, server.position[1] - 15, 30, 30))
                self.draw_text(server.name, 12, server.position[0], server.position[1] + 20)
        pos = self.player.current_server.position
        pg.draw.rect(self.screen, COLOR_CURSOR, (pos[0] - 20, pos[1] - 20, 40, 40), 2)

    def draw_trace_bar(self):
        map_area_x = WIDTH * 0.62
        trace_percent_raw = self.system_trace
        trace_percent_display = int(trace_percent_raw * 100)
        trace_percent_clamped = max(0.0, min(1.0, trace_percent_raw))
        r = int(min(255, 255 * (trace_percent_clamped * 2)))
        g = int(min(255, 510 * (1 - trace_percent_clamped)))
        b = 0
        trace_color = (r, g, b)
        trace_text = f"SYSTEM TRACE: {trace_percent_display}%"
        self.draw_text(trace_text, 18, map_area_x, 20, align="topleft")
        pg.draw.rect(self.screen, (50,50,50), (map_area_x, 45, WIDTH - map_area_x - 20, 20))
        pg.draw.rect(self.screen, trace_color, (map_area_x, 45, (WIDTH - map_area_x - 20) * trace_percent_clamped, 20))

    def draw_text(self, text, size, x, y, align="midtop"):
        font = pg.font.Font(None, size)
        text_surface = font.render(text, True, COLOR_TEXT)
        text_rect = text_surface.get_rect()
        if align == "midtop": text_rect.midtop = (x, y)
        elif align == "topleft": text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)

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
        
        handler = COMMAND_MAP.get(command_name)
        if handler:
            handler(self, args)
        else:
            self.console.history.append(f"  -bash: command not found: {command_name}")

        if self.game_active:
            self.check_game_over_conditions()

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
