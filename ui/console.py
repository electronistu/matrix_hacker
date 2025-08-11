import pygame as pg
from settings import WIDTH, HEIGHT, COLOR_TEXT, COLOR_CURSOR

class Console:
    def __init__(self, game):
        self.game = game
        self.input_text = ""
        self.history = []
        self.font = pg.font.Font(pg.font.match_font('monospace'), 16)
        self.cursor_visible = True
        self.cursor_timer = 0
        self.is_password_prompt = False
        self.password_callback = None
        self.scroll_offset = 0

    def get_prompt(self):
        if self.is_password_prompt:
            return "password: "
        path = self.game.get_current_path()
        return f"[{self.game.player.user}@{self.game.player.current_server.name} {path}]$ "

    def handle_event(self, event):
        if event.type == pg.MOUSEWHEEL:
            self.scroll_offset += event.y
            if self.scroll_offset > len(self.history) - 5:
                self.scroll_offset = len(self.history) - 5
            if self.scroll_offset < 0:
                self.scroll_offset = 0
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                self.process_command()
            elif event.key == pg.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                self.input_text += event.unicode

    def process_command(self):
        command_full = self.input_text.strip()
        if self.is_password_prompt:
            self.history.append(self.get_prompt() + "********")
            self.is_password_prompt = False
            self.password_callback(command_full)
            self.input_text = ""
            return

        self.history.append(self.get_prompt() + command_full)
        self.game.execute_command(command_full)
        self.input_text = ""
        self.scroll_offset = 0 # Reset scroll on new command

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface, console_width): # Added console_width parameter
        # console_width = WIDTH * 0.58 # Removed, now passed as argument
        y_pos = HEIGHT - 30
        prompt = self.get_prompt()
        display_text = prompt + self.input_text if not self.is_password_prompt else prompt + "*" * len(self.input_text)
        input_surface = self.font.render(display_text, True, COLOR_TEXT)
        surface.blit(input_surface, (10, y_pos))

        if self.cursor_visible:
            cursor_pos = self.font.size(display_text)[0] + 10
            pg.draw.rect(surface, COLOR_CURSOR, (cursor_pos, y_pos, 10, 18))

        draw_y = y_pos
        display_history = self.history[-(25 + self.scroll_offset):-self.scroll_offset if self.scroll_offset > 0 else None]
        for line in reversed(display_history):
            if draw_y < 25: break
            words = line.split(' ')
            wrapped_lines = []
            current_line = ""
            for word in words:
                if self.font.size(current_line + word)[0] < console_width: # Use passed console_width
                    current_line += word + " "
                else:
                    wrapped_lines.append(current_line)
                    current_line = word + " "
            wrapped_lines.append(current_line)

            for sub_line in reversed(wrapped_lines):
                if draw_y < 25: break
                history_surface = self.font.render(sub_line, True, COLOR_TEXT)
                surface.blit(history_surface, (10, draw_y - 22))
                draw_y -= 22
