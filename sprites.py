# L.I.C. Matrix - Sprites

import pygame as pg
import random
from settings import *

class Node(pg.sprite.Sprite):
    def __init__(self, game, x, y, node_type):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.node_type = node_type

        self.image = pg.Surface((32, 32))
        self.image.set_colorkey((0,0,0)) # Make black transparent
        self.rect = self.image.get_rect()
        self.rect.x = x * 64 + 100
        self.rect.y = y * 64 + 100

        self.is_hovered = False
        self.is_processed = False # For Genesis nodes

        self.set_color()
        self.draw_node()

    def set_color(self):
        if self.node_type == 'fragment':
            self.color = COLOR_NODE_FRAGMENT
        elif self.node_type == 'genesis':
            self.color = COLOR_NODE_GENESIS
        elif self.node_type == 'paradox':
            self.color = COLOR_PARADOX
        elif self.node_type == 'chaos':
            self.color = COLOR_CHAOS
        elif self.node_type == 'anchor':
            self.color = COLOR_ANCHOR
        else:
            self.color = COLOR_NODE_DEFAULT

    def draw_node(self):
        display_color = self.color
        if self.is_hovered:
            # Brighten the color on hover
            display_color = tuple(min(c + 50, 255) for c in self.color)
        if self.is_processed:
            display_color = COLOR_ARCHITECT # Turn white when processed

        self.image.fill((0,0,0))
        pg.draw.circle(self.image, display_color, (16, 16), 16)

    def update(self):
        # Check for hover
        self.is_hovered = self.rect.collidepoint(pg.mouse.get_pos())
        self.draw_node()

    def on_click(self):
        print(f"Node ({self.x}, {self.y}) of type '{self.node_type}' selected.")
        # Implement effects based on type
        if self.node_type == 'anchor':
            effectiveness = 0.2 + (self.game.profile['upgrades']['anchor_effectiveness_increase'] * 0.05)
            self.game.cognitive_load -= effectiveness
        elif self.node_type == 'paradox':
            self.game.cognitive_load += 0.3
        elif self.node_type == 'chaos':
            if random.random() < 0.5:
                self.game.cognitive_load -= 0.5
            else:
                self.game.cognitive_load += 0.5
        elif self.node_type == 'fragment':
            self.game.collect_fragment(self)
            self.is_processed = True
            # No cognitive load change for processing a genesis node itself
        else: # Default node
            self.game.cognitive_load += 0.1
        
        # Ensure load stays within bounds 0-1
        if self.game.cognitive_load < 0:
            self.game.cognitive_load = 0
        if self.game.cognitive_load > 1:
            self.game.cognitive_load = 1
