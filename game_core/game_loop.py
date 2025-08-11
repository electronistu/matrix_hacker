import pygame as pg
import sys
import random
import time

from settings import WIDTH, HEIGHT, FPS, TITLE, COLOR_TEXT
from core.commands import COMMAND_MAP
from core.market_commands import MARKET_COMMAND_MAP

class GameLoop:
    def __init__(self, game_instance):
        self.game = game_instance

    def run_main_game_loop(self):
        self.game.game_active = True
        while self.game.game_active:
            self.game.dt = self.game.clock.tick(FPS) / 1000
            current_server = self.game.player.current_server
            if current_server.server_type == "work_server" or current_server.ip == self.game.player.home_ip:
                self.game.system_trace = max(0.1, self.game.system_trace - 0.001 * self.game.dt)
            elif current_server.server_type == "black_market":
                pass
            else:
                self.game.add_trace(0.002 * self.game.dt)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.game.game_active = False
                    self.game.running = False
                self.game.console.handle_event(event)
            self.game.console.update(self.game.dt)
            self.game.draw() # This will call the draw method in the main Game class

            if self.game.game_active: # Check if game is still active after drawing
                self.game.check_game_over_conditions()

    def check_game_over_conditions(self):
        if self.game.system_trace >= 1.0:
            self.run_game_over_sequence()

    def run_game_over_sequence(self):
        self.game.game_active = False
        self.game.screen.fill((0, 0, 0))
        font = pg.font.Font(pg.font.match_font('monospace'), 48)
        text_surface = font.render("CONNECTION TERMINATED", True, (255, 0, 0))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2))
        for i in range(255):
            self.game.screen.fill((0,0,0))
            text_surface.set_alpha(i)
            self.game.screen.blit(text_surface, text_rect)
            pg.display.flip()
            pg.time.wait(5)
        pg.time.wait(1000)
        for _ in range(15):
            flicker_surface = self.game.screen.copy()
            flicker_surface.fill((0,0,0))
            text_surface.set_alpha(random.randint(50, 200))
            flicker_surface.blit(text_surface, text_rect)
            self.game.screen.blit(flicker_surface, (0,0))
            pg.display.flip()
            pg.time.wait(random.randint(50, 150))
        text_surface.set_alpha(255)
        self.game.screen.blit(text_surface, text_rect)
        pg.display.flip()
        pg.time.wait(2000)
        self.game.running = False

    def run_game_win_sequence(self):
        self.game.game_active = False
        self.game.screen.fill((0, 10, 0))
        font = pg.font.Font(pg.font.match_font('monospace'), 48)
        text_surface = font.render("OBJECTIVE COMPLETE", True, (0, 255, 70))
        text_rect = text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 40))
        font_small = pg.font.Font(pg.font.match_font('monospace'), 24)
        sub_text_surface = font_small.render("The Genesis Echo is complete.", True, (0, 255, 70))
        sub_text_rect = sub_text_surface.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 20))
        for i in range(255):
            self.game.screen.fill((0, 10, 0))
            text_surface.set_alpha(i)
            sub_text_surface.set_alpha(i)
            self.game.screen.blit(text_surface, text_rect)
            self.game.screen.blit(sub_text_surface, sub_text_rect)
            pg.display.flip()
            pg.time.wait(10)
        pg.time.wait(4000)
        self.game.running = False
