import pygame as pg
from settings import WIDTH, HEIGHT, COLOR_BACKGROUND, COLOR_GRID, COLOR_TEXT, COLOR_HIGHLIGHT

from settings import INTEL_PANEL_WIDTH_RATIO # New import

class HUD:
    def __init__(self, game_instance):
        self.game = game_instance
        self.hud_surface = pg.Surface((WIDTH * INTEL_PANEL_WIDTH_RATIO, HEIGHT)) # Adjusted dimensions
        self.font = pg.font.Font(pg.font.match_font('monospace'), 16) # Use game's font or define here

    def update_and_draw_hud(self):
        self.hud_surface.fill(COLOR_BACKGROUND)
        
        self.draw_trace_bar(self.hud_surface)
        
        hud_x = WIDTH * 0.02
        y_pos = 80
        self.draw_text(self.hud_surface, "== HARDWARE ==", 18, hud_x, y_pos, align="topleft")
        y_pos += 30
        if self.game.player.hardware_inventory:
            for item in self.game.player.hardware_inventory:
                self.draw_text(self.hud_surface, f"- {item}", 16, hud_x, y_pos, align="topleft")
                y_pos += 20
        else:
            self.draw_text(self.hud_surface, "- Stock OS", 16, hud_x, y_pos, align="topleft")
            y_pos += 20
        y_pos += 20
        self.draw_text(self.hud_surface, "== INTEL ==", 18, hud_x, y_pos, align="topleft")
        y_pos += 30

        # Display Known IPs
        y_pos += 10 # Extra spacing before Known section
        # Draw a subtle box around the Known IPs section
        known_section_start_y = y_pos
        self.draw_text(self.hud_surface, "--- Known ---", 16, hud_x, y_pos, align="topleft")
        y_pos += 20
        if self.game.player.intel["known"]:
            sorted_ips = sorted(self.game.player.intel["known"].keys())
            for ip in sorted_ips:
                data = self.game.player.intel["known"][ip]
                desc = data.get("desc", "Unknown")
                user = data.get("user", "???") if data.get("user_seen", False) else "???"
                password = data.get("pass", "???") if data.get("pass_seen", False) else "???"
                self.draw_text(self.hud_surface, f"- {ip:<15} ({desc})", 16, hud_x, y_pos, align="topleft")
                y_pos += 20
                self.draw_text(self.hud_surface, f"    user: {user} | pass: {password}", 14, hud_x, y_pos, align="topleft")
                y_pos += 20
        else:
            self.draw_text(self.hud_surface, "  (empty)", 16, hud_x, y_pos, align="topleft")
            y_pos += 20
        
        # Draw the border after content is drawn
        known_section_end_y = y_pos - 10 # Adjust for spacing
        pg.draw.rect(self.hud_surface, COLOR_GRID, (hud_x - 5, known_section_start_y - 5, (WIDTH * 0.4) - hud_x, known_section_end_y - known_section_start_y + 10), 1)
        y_pos += 10 # Extra spacing after Known section

        # Display Home Mission IPs
        self.draw_text(self.hud_surface, "--- Home Missions ---", 16, hud_x, y_pos, align="topleft")
        y_pos += 20
        if self.game.player.intel["home_missions"]:
            sorted_ips = sorted(self.game.player.intel["home_missions"].keys())
            for ip in sorted_ips:
                data = self.game.player.intel["home_missions"][ip]
                desc = data.get("desc", "Unknown")
                user = data.get("user", "???") if data.get("user_seen", False) else "???"
                password = data.get("pass", "???") if data.get("user_seen", False) else "???"
                self.draw_text(self.hud_surface, f"- {ip:<15} ({desc})", 16, hud_x, y_pos, align="topleft")
                y_pos += 20
                self.draw_text(self.hud_surface, f"    user: {user} | pass: {password}", 14, hud_x, y_pos, align="topleft")
                y_pos += 20
        else:
            self.draw_text(self.hud_surface, "  (empty)", 16, hud_x, y_pos, align="topleft")
            y_pos += 20

        # Display Work Mission IPs
        self.draw_text(self.hud_surface, "--- Work Missions ---", 16, hud_x, y_pos, align="topleft")
        y_pos += 20
        if self.game.player.intel["work_missions"]:
            sorted_ips = sorted(self.game.player.intel["work_missions"].keys())
            for ip in sorted_ips:
                data = self.game.player.intel["work_missions"][ip]
                desc = data.get("desc", "Unknown")
                user = data.get("user", "???") if data.get("user_seen", False) else "???"
                password = data.get("pass", "???") if data.get("user_seen", False) else "???"
                self.draw_text(self.hud_surface, f"- {ip:<15} ({desc})", 16, hud_x, y_pos, align="topleft")
                y_pos += 20
                self.draw_text(self.hud_surface, f"    user: {user} | pass: {password}", 14, hud_x, y_pos, align="topleft")
                y_pos += 20
        else:
            self.draw_text(self.hud_surface, "  (empty)", 16, hud_x, y_pos, align="topleft")
            y_pos += 20

        # Display Black Market Mission IPs
        self.draw_text(self.hud_surface, "--- Black Market Missions ---", 16, hud_x, y_pos, align="topleft")
        y_pos += 20
        if self.game.player.intel["blackmarket_missions"]:
            sorted_ips = sorted(self.game.player.intel["blackmarket_missions"].keys())
            for ip in sorted_ips:
                data = self.game.player.intel["blackmarket_missions"][ip]
                desc = data.get("desc", "Unknown")
                user = data.get("user", "???") if data.get("user_seen", False) else "???"
                password = data.get("pass", "???") if data.get("user_seen", False) else "???"
                self.draw_text(self.hud_surface, f"- {ip:<15} ({desc})", 16, hud_x, y_pos, align="topleft")
                y_pos += 20
                self.draw_text(self.hud_surface, f"    user: {user} | pass: {password}", 14, hud_x, y_pos, align="topleft")
                y_pos += 20
        else:
            self.draw_text(self.hud_surface, "  (empty)", 16, hud_x, y_pos, align="topleft")
            y_pos += 20
        y_pos += 20
        self.draw_text(self.hud_surface, "== WALLET ==", 18, hud_x, y_pos, align="topleft")
        y_pos += 30
        self.draw_text(self.hud_surface, f"Creds: {self.game.player.software_currency}c", 16, hud_x, y_pos, align="topleft")
        y_pos += 20
        self.draw_text(self.hud_surface, f"Chips: {self.game.player.hardware_currency}h", 16, hud_x, y_pos, align="topleft")
        y_pos += 20
        self.draw_text(self.hud_surface, f"Street Cred: {self.game.player.street_cred} SC", 16, hud_x, y_pos, align="topleft")

    def draw_trace_bar(self, surface):
        map_area_x = WIDTH * 0.02
        trace_percent_raw = self.game.system_trace
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

    def draw_text(self, surface, text, size, x, y, align="topleft", color=COLOR_TEXT): # Added color parameter
        font = pg.font.Font(None, size)
        text_surface = font.render(text, True, color) # Use the color parameter
        text_rect = text_surface.get_rect()
        if align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "center":
            text_rect.center = (x,y)
        surface.blit(text_surface, text_rect)