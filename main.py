import pygame as pg
import sys
from game import Game

def main():
    """Main function to run the game."""
    pg.init()
    game = Game()
    game.new_game()
    pg.quit()
    sys.exit()

if __name__ == '__main__':
    main()