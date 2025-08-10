import pygame as pg
import sys
from game import Game
import profile_manager
from settings import *

def draw_text(surface, text, size, x, y, color, align="center"):
    """Helper function to draw text on the menu screen."""
    font = pg.font.Font(pg.font.match_font('monospace'), size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if align == "center":
        text_rect.center = (x, y)
    elif align == "topleft":
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def main_menu(screen):
    """Displays the main menu and handles user choice."""
    menu_active = True
    
    has_save = profile_manager.has_save_file()

    while menu_active:
        screen.fill(COLOR_BACKGROUND)
        draw_text(screen, "Matrix Hacker", 64, WIDTH / 2, HEIGHT / 4, COLOR_TEXT)
        
        if has_save:
            draw_text(screen, "(L)oad Previous Game", 22, WIDTH / 2, HEIGHT / 2, COLOR_TEXT)
            draw_text(screen, "(S)tart a New Game", 22, WIDTH / 2, HEIGHT / 2 + 40, COLOR_TEXT)
        else:
            draw_text(screen, "(S)tart a New Game", 22, WIDTH / 2, HEIGHT / 2 + 20, COLOR_TEXT)

        pg.display.flip()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return "QUIT"
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_s:
                    if has_save:
                        profile_manager.delete_profile()
                    return "NEW_GAME"
                if event.key == pg.K_l and has_save:
                    return "LOAD_GAME"
    return "QUIT"


def main():
    """Main function to run the game."""
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption(TITLE)
    
    choice = main_menu(screen)
    
    if choice == "QUIT":
        pg.quit()
        sys.exit()

    game = Game()
    
    if choice == "NEW_GAME":
        profile = profile_manager.get_default_profile()
        game.new_game(profile)
    elif choice == "LOAD_GAME":
        profile = profile_manager.load_profile()
        game.new_game(profile)

    # Save profile on graceful exit
    if game.running is False:
        profile_manager.save_profile(game.player)

    pg.quit()
    sys.exit()

if __name__ == '__main__':
    main()
