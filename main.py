# Matrix Hacker - Main

import pygame as pg
import sys
import re
import random
import time

# --- SETTINGS ---
WIDTH, HEIGHT = 1280, 720
FPS = 60
TITLE = "Matrix Hacker"
COLOR_BACKGROUND = (0, 10, 0)
COLOR_TEXT = (0, 255, 70)
COLOR_GRID = (0, 80, 0)
COLOR_CURSOR = (0, 255, 70)
COLOR_NODE_ROOT = (255, 255, 0)
COLOR_NODE_FIREWALL = (255, 0, 0)
COLOR_NODE_DATA = (0, 150, 255)
COLOR_NODE_DEFAULT = (0, 180, 70)

# --- FILESYSTEM CLASSES ---
class File:
    def __init__(self, name, content=""):
        self.name = name
        self.content = content
        self.parent = None

class Directory:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = {}

    def add_child(self, child):
        child.parent = self
        self.children[child.name] = child

    def get_child(self, name):
        return self.children.get(name)

# --- SERVER CLASS ---
class Server:
    def __init__(self, ip, name, server_type='default', position=(0,0)):
        self.ip = ip
        self.name = name
        self.server_type = server_type
        self.position = position
        self.is_discovered = False
        self.accounts = {}
        self.fs = Directory('/')
        self.fs.add_child(Directory('home'))
        self.fs.add_child(Directory('var'))
        self.fs.add_child(Directory('bin'))
        self.vulnerability_found = False

    def add_user(self, user, password):
        self.accounts[user] = password
        home_dir = self.fs.get_child('home')
        if not home_dir.get_child(user):
            home_dir.add_child(Directory(user))

# --- PLAYER CLASS ---
class Player:
    def __init__(self, starting_server):
        self.current_server = starting_server
        self.current_directory = starting_server.fs
        self.user = "operative"
        self.commands = ["help", "ls", "dir", "cat", "cd", "pwd"]

# --- CONSOLE CLASS ---
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

    def draw(self, surface):
        console_width = WIDTH * 0.58
        y_pos = HEIGHT - 30
        prompt = self.get_prompt()
        display_text = prompt + self.input_text if not self.is_password_prompt else prompt + "*" * len(self.input_text)
        input_surface = self.font.render(display_text, True, COLOR_TEXT)
        surface.blit(input_surface, (10, y_pos))

        if self.cursor_visible:
            cursor_pos = self.font.size(display_text)[0] + 10
            pg.draw.rect(surface, COLOR_CURSOR, (cursor_pos, y_pos, 10, 18))

        draw_y = y_pos
        # Use a slice of history based on scroll offset
        display_history = self.history[-(25 + self.scroll_offset):-self.scroll_offset if self.scroll_offset > 0 else None]
        for line in reversed(display_history):
            if draw_y < 25: break
            words = line.split(' ')
            wrapped_lines = []
            current_line = ""
            for word in words:
                if self.font.size(current_line + word)[0] < console_width:
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

# --- MAIN GAME CLASS ---
class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.running = True
        self.font = pg.font.Font(pg.font.match_font('monospace'), 16)

    def new_game(self):
        self.system_trace = 0.1
        self.servers = {}
        self.generate_network()
        self.player = Player(self.servers["127.0.0.1"])
        self.console = Console(self)
        self.console.history.extend([
            ">>> SECURE CONNECTION ESTABLISHED...",
            "Control: Operative, you're in. Your mission is in 'mission.txt'.",
            "Control: Before you read it, you need to learn to navigate.",
            "Control: The 'bin' directory contains help files for commands.",
            "Control: Use 'ls /bin' to see them, then 'cat /bin/cd.hlp' to learn how to move."
        ])
        self.run_main_game_loop()

    def generate_network(self):
        # Create local server
        local_server = Server("127.0.0.1", "local-node", position=(int(WIDTH*0.8), HEIGHT // 2))
        local_server.is_discovered = True
        local_server.add_user('operative', '')
        self.servers["127.0.0.1"] = local_server

        # Procedurally generate the rest of the network
        num_servers = random.randint(10, 15)
        server_ips = [f"10.1.{random.randint(1,254)}.{random.randint(1,254)}" for _ in range(num_servers)]
        server_names = [f"node-0{i}" for i in range(num_servers)]
        server_types = ['data'] * 4 + ['firewall'] * 2 + ['default'] * (num_servers - 7) + ['root']
        random.shuffle(server_types)

        # Create servers
        for i in range(num_servers):
            pos_x = int(WIDTH * 0.8 + random.randint(-150, 150))
            pos_y = int(HEIGHT / 2 + random.randint(-300, 300))
            self.servers[server_ips[i]] = Server(server_ips[i], server_names[i], server_types[i], (pos_x, pos_y))

        # Create a solvable path of clues
        path = random.sample(server_ips, 5)
        root_server_ip = None
        for ip in server_ips:
            if self.servers[ip].server_type == 'root':
                root_server_ip = ip
                if root_server_ip in path:
                    path.remove(root_server_ip)
                break
        path.append(root_server_ip)

        # Plant clues and lore
        local_server.fs.get_child('home').get_child('operative').add_child(File("mission.txt", f"OBJECTIVE: Infiltrate the ghost network 'Aethelred' and find the Genesis report.\n\nYour first clue is on the gateway server. Its IP is {path[0]}. You'll need to learn how to connect to it. Look for help files in /bin."))
        local_server.fs.get_child('bin').add_child(File("ssh.hlp", "COMMAND: ssh <user>@<ip>\nConnects to a remote server. Requires a username and IP address. Some accounts may require a password."))
        local_server.fs.get_child('bin').add_child(File("cd.hlp", "COMMAND: cd <path>\nChanges directory. '.' is the current dir, '..' is the parent. '~' is your home directory (/home/user). You can use absolute or relative paths."))
        local_server.fs.get_child('bin').add_child(File("pwd.hlp", "COMMAND: pwd\nPrints the full path of your current working directory."))

        # Gateway Server
        gw_server = self.servers[path[0]]
        gw_server.add_user('guest', 'guest')
        gw_server.fs.get_child('home').get_child('guest').add_child(File("readme.txt", f"ADMIN_NOTE: Johnson, you idiot. You left the password for the file server ({path[1]}) on a post-it note AGAIN. I've hidden the credentials for the 'archivist' account in your home directory. Get it and delete the file. And for god's sake, stop using your dog's name as the password!\n"))
        gw_server.fs.get_child('home').add_child(Directory('johnson'))
        gw_server.fs.get_child('home').get_child('johnson').add_child(File("credentials.bak", "user: archivist | pass: buddy"))
        
        # File Server
        fs_server = self.servers[path[1]]
        fs_server.add_user('archivist', 'buddy')
        fs_server.fs.get_child('home').get_child('archivist').add_child(File("project_note.txt", f"The L.I.C. Matrix is unstable. The next server in the chain is {path[2]}, but it's behind a firewall. You'll need to find a vulnerability. Run a port scan.\nRKSE_LOG: The Cognitive Load is nearing the 503_Stall threshold."))
        fs_server.fs.get_child('bin').add_child(File("nmap.hlp", "COMMAND: nmap <ip>\nScans a target IP for open ports and potential vulnerabilities. Increases trace significantly."))

        # Firewall Server
        fw_server = self.servers[path[2]]
        fw_server.add_user('admin', 'adminpass')
        fw_server.fs.get_child('home').get_child('admin').add_child(File("firewall_config.txt", f"Firewall is active. All ports are blocked except for SSH on port 22. The database server at {path[3]} is on the internal network."))

        # Penultimate Server
        penultimate_server = self.servers[path[3]]
        penultimate_server.add_user('db_admin', 'secure_password')
        penultimate_server.fs.get_child('home').get_child('db_admin').add_child(File("final_clue.txt", f"The root server is at {path[4]}. The password is what the Architect always told K_Prime to do."))
        penultimate_server.fs.get_child('home').get_child('db_admin').add_child(File("chat_log_R-K.txt", "R_Prime: Kelly, you have to trust the process.\nK_Prime: The process is flawed!"))

        # Root Server
        root_server = self.servers[path[4]]
        root_server.add_user('root', 'TrustTheProcess')
        root_server.fs.get_child('home').get_child('root').add_child(File("P_Foundational_v5.1.txt", "[ACCESS GRANTED] Welcome, Architect."))

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
        pg.draw.rect(self.screen, (0,5,0), (0, 0, WIDTH * 0.6, HEIGHT))
        self.draw_network_map()
        self.draw_trace_bar()
        self.console.draw(self.screen)
        pg.display.flip()

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
        # Interpolate color from green to yellow to red
        r = int(min(255, 255 * (self.system_trace * 2)))
        g = int(min(255, 510 * (1 - self.system_trace)))
        b = 0
        trace_color = (r, g, b)

        trace_text = f"SYSTEM TRACE: {int(self.system_trace * 100)}%"
        self.draw_text(trace_text, 18, map_area_x, 20, align="topleft")
        pg.draw.rect(self.screen, (50,50,50), (map_area_x, 45, WIDTH - map_area_x - 20, 20))
        pg.draw.rect(self.screen, trace_color, (map_area_x, 45, (WIDTH - map_area_x - 20) * self.system_trace, 20))

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

    def resolve_path(self, path_str):
        if not path_str:
            return self.player.current_directory

        if path_str.startswith('~'):
            home_path = f"/home/{self.player.user}"
            path_str = path_str.replace('~', home_path, 1)

        current_node = self.player.current_directory
        if path_str.startswith('/'):
            current_node = self.player.current_server.fs
            path_parts = path_str.strip('/').split('/')
        else:
            path_parts = path_str.split('/')

        if path_parts == ['']: return current_node

        for part in path_parts:
            if part == '..':
                if current_node.parent:
                    current_node = current_node.parent
            elif part != '.' and part != '':
                next_node = current_node.get_child(part)
                if next_node:
                    current_node = next_node
                else:
                    return None
        return current_node

    def execute_command(self, command_full):
        parts = command_full.split()
        if not parts: return
        command = parts[0]
        args = parts[1:]
        
        if command in self.player.commands:
            if command == "help": self.console.history.append(f'  Commands: {" ".join(self.player.commands)}')
            elif command in ["ls", "dir"]: self.execute_ls(args)
            elif command == "cd": self.execute_cd(args)
            elif command == "pwd": self.console.history.append(self.get_current_path())
            elif command == "cat": self.execute_cat(args)
            elif command == "ssh": self.execute_ssh(args)
            elif command == "nmap": self.execute_nmap(args)
            elif command == "exit": self.game_active = False
        else:
            self.console.history.append(f"  -bash: command not found: {command}")

    def execute_ls(self, args):
        path = args[0] if args else "."
        target_dir = self.resolve_path(path)
        if isinstance(target_dir, Directory):
            output = "  ".join(target_dir.children.keys())
            self.console.history.append(output if output else "  (empty)")
        elif target_dir is None:
            self.console.history.append(f"  ls: cannot access '{path}': No such file or directory")
        else:
            self.console.history.append(path.split('/')[-1])

    def execute_cd(self, args):
        if not args: path = '~';
        else: path = args[0]
        
        target_dir = self.resolve_path(path)
        if isinstance(target_dir, Directory):
            self.player.current_directory = target_dir
        else:
            self.console.history.append(f"  cd: no such directory: {path}")

    def execute_cat(self, args):
        if not args: self.console.history.append("  usage: cat <file>"); return
        path = args[0]
        target_file = self.resolve_path(path)
        if isinstance(target_file, File):
            filename = path.split('/')[-1]
            if filename.endswith(".hlp"):
                command_name = filename.split('.')[0]
                if command_name not in self.player.commands:
                    self.player.commands.append(command_name)
                    self.console.history.append(f"  New command learned: {command_name}")
            
            if self.player.current_server.server_type == 'root' and filename == 'P_Foundational_v5.1.txt':
                if self.player.current_server.vulnerability_found:
                    self.console.history.extend(["  --- ACCESSING CORE MEMORY ---", target_file.content, "  -------------------------", "*** THE GENESIS CIPHER -- OBJECTIVE COMPLETE ***"])
                    time.sleep(2)
                    self.game_active = False
                else:
                    self.console.history.append("  cat: P_Foundational_v5.1.txt: File is encrypted. A vulnerability is required."); self.system_trace += 0.1
            else:
                self.console.history.extend([f"  --- Contents of {filename} ---", target_file.content, "  -------------------------"])
        else:
            self.console.history.append(f"  cat: cannot access '{path}': No such file or directory")

    def execute_nmap(self, args):
        if not args: self.console.history.append("  usage: nmap <ip_address>"); return
        target_ip = args[0]
        if target_ip not in self.servers: self.console.history.append("  Host not found."); return
        
        self.console.history.append(f"  Scanning {target_ip}... Trace increased."); self.system_trace += 0.15
        target_server = self.servers[target_ip]
        if target_server.server_type == 'root':
            self.console.history.append("  VULNERABILITY DETECTED: Port 22 open with outdated SSH version. Encryption can be bypassed.")
            target_server.vulnerability_found = True
        else:
            self.console.history.append("  Scan complete. No obvious vulnerabilities found.")

    def execute_ssh(self, args):
        if not args: self.console.history.append("  usage: ssh <user>@<ip_address>"); return
        match = re.match(r"(\w+)@([\d\.]+)", args[0])
        if not match: self.console.history.append("  usage: ssh <user>@<ip_address>"); return
        user, ip = match.groups()
        if ip not in self.servers: self.console.history.append(f"  ssh: connect to host {ip} port 22: Connection refused"); self.system_trace += 0.05; return
        
        target_server = self.servers[ip]
        target_server.is_discovered = True
        if user not in target_server.accounts: self.console.history.append(f"  Permission denied (publickey,password)."); self.system_trace += 0.1; return
        
        if target_server.accounts.get(user) == 'guest':
            self.console.history.append(f"  Authentication successful. Welcome to {target_server.name}.")
            self.player.current_server = target_server; self.player.current_directory = target_server.fs; self.player.user = user
            return

        self.console.is_password_prompt = True
        def check_password(password):
            if target_server.accounts.get(user) == password:
                self.console.history.append(f"  Authentication successful. Welcome to {target_server.name}.")
                self.player.current_server = target_server; self.player.current_directory = target_server.fs; self.player.user = user
            else: self.console.history.append("  Permission denied, please try again."); self.system_trace += 0.15
        self.console.password_callback = check_password

if __name__ == '__main__':
    g = Game()
    g.new_game()
    pg.quit()
    sys.exit()