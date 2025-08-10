import re
import time
from core.filesystem import Directory, File

def resolve_path(game, path_str):
    if not path_str:
        return game.player.current_directory
    if path_str.startswith('~'):
        home_path = f"/home/{game.player.user}"
        path_str = path_str.replace('~', home_path, 1)
    
    current_node = game.player.current_directory
    if path_str.startswith('/'):
        current_node = game.player.current_server.fs
        path_parts = path_str.strip('/').split('/')
    else:
        path_parts = path_str.split('/')
    
    if path_parts == ['']:
        return current_node
        
    for i, part in enumerate(path_parts):
        if part == '..':
            if current_node.parent:
                current_node = current_node.parent
        elif part != '.' and part != '':
            next_node = current_node.get_child(part)
            if next_node:
                if i == len(path_parts) - 1:
                    return next_node
                elif isinstance(next_node, Directory):
                    current_node = next_node
                else:
                    return None # Path goes through a file
            else:
                return None
    return current_node

def handle_help(game, args):
    game.console.history.append(f'  Commands: {" ".join(sorted(game.player.commands))}')

def handle_pwd(game, args):
    game.console.history.append(game.get_current_path())

def handle_ls(game, args):
    path = args[0] if args else "."
    target_dir = resolve_path(game, path)
    if isinstance(target_dir, Directory):
        game.console.history.append("  ".join(target_dir.children.keys()) or "  (empty)")
    elif target_dir is None:
        game.console.history.append(f"  ls: cannot access '{path}': No such file or directory")
    else:
        game.console.history.append(path.split('/')[-1])

def handle_cd(game, args):
    if not args:
        path = '~'
    else:
        path = args[0]
    target_dir = resolve_path(game, path)
    if isinstance(target_dir, Directory):
        game.player.current_directory = target_dir
    else:
        game.console.history.append(f"  cd: no such directory: {path}")

def handle_cat(game, args):
    if not args:
        game.console.history.append("  usage: cat <file>")
        return
    path = args[0]
    target_file = resolve_path(game, path)
    if isinstance(target_file, File):
        filename = path.split('/')[-1]
        if filename.endswith(".hlp"):
            command_name = filename.split('.')[0]
            if command_name not in game.player.commands:
                game.player.commands.append(command_name)
                game.console.history.append(f"  New command learned: {command_name}")
        
        if game.player.current_server.server_type == 'root' and filename == 'P_Foundational_v5.1.txt':
            if game.player.current_server.vulnerability_found:
                game.console.history.extend([
                    "  --- ACCESSING CORE MEMORY ---",
                    target_file.content,
                    "  -------------------------",
                    "*** THE GENESIS CIPHER -- OBJECTIVE COMPLETE ***"
                ])
                time.sleep(2)
                game.game_active = False
            else:
                game.console.history.append("  cat: P_Foundational_v5.1.txt: File is encrypted. A vulnerability is required.")
                game.system_trace += 0.1
        else:
            game.console.history.extend([
                f"  --- Contents of {filename} ---",
                target_file.content,
                "  -------------------------"
            ])
    else:
        game.console.history.append(f"  cat: cannot access '{path}': No such file or directory")

def handle_nmap(game, args):
    if not args:
        game.console.history.append("  usage: nmap <ip_address>")
        return
    target_ip = args[0]
    if target_ip not in game.servers:
        game.console.history.append("  Host not found.")
        return
    
    game.console.history.append(f"  Scanning {target_ip}... Trace increased.")
    game.system_trace += 0.15
    target_server = game.servers[target_ip]
    
    if target_server.server_type == 'root':
        game.console.history.append("  VULNERABILITY DETECTED: Port 22 open with outdated SSH version. Encryption can be bypassed.")
        target_server.vulnerability_found = True
    else:
        game.console.history.append("  Scan complete. No obvious vulnerabilities found.")

def handle_ssh(game, args):
    if not args:
        game.console.history.append("  usage: ssh <user>@<ip_address>")
        return
    
    match = re.match(r"(\w+)@([\d\.]+)", args[0])
    if not match:
        game.console.history.append("  usage: ssh <user>@<ip_address>")
        return
        
    user, ip = match.groups()
    if ip not in game.servers:
        game.console.history.append(f"  ssh: connect to host {ip} port 22: Connection refused")
        game.system_trace += 0.05
        return
        
    target_server = game.servers[ip]
    target_server.is_discovered = True
    
    if user not in target_server.accounts:
        game.console.history.append(f"  Permission denied (publickey,password).")
        game.system_trace += 0.1
        return

    if target_server.accounts.get(user) == 'guest' or not target_server.accounts.get(user):
        game.console.history.append(f"  Authentication successful. Welcome to {target_server.name}.")
        game.player.current_server = target_server
        game.player.current_directory = target_server.fs
        game.player.user = user
        return

    game.console.is_password_prompt = True
    def check_password(password):
        if target_server.accounts.get(user) == password:
            game.console.history.append(f"  Authentication successful. Welcome to {target_server.name}.")
            game.player.current_server = target_server
            game.player.current_directory = target_server.fs
            game.player.user = user
        else:
            game.console.history.append("  Permission denied, please try again.")
            game.system_trace += 0.15
    game.console.password_callback = check_password

def handle_grep(game, args):
    """Handles the 'grep' command."""
    if len(args) < 2:
        game.console.history.append("  usage: grep <pattern> <file>")
        return
    pattern, file_path = args[0], args[1]
    target_file = resolve_path(game, file_path)
    if isinstance(target_file, File):
        matches = []
        for line in target_file.content.splitlines():
            if re.search(pattern, line, re.IGNORECASE):
                matches.append(f"  > {line}")
        if matches:
            game.console.history.extend(matches)
    else:
        game.console.history.append(f"  grep: {file_path}: No such file or directory")

def handle_tcpdump(game, args):
    """Handles the 'tcpdump' command."""
    capture_file = game.player.current_server.fs.get_child(".tcp_capture")
    if isinstance(capture_file, File):
        game.console.history.append(f"--- BEGINNING PACKET CAPTURE ON {game.player.current_server.name} ---")
        game.console.history.extend(f"  {line}" for line in capture_file.content.splitlines())
        game.console.history.append("--- END PACKET CAPTURE ---")
        game.system_trace += 0.2
    else:
        game.console.history.append("  tcpdump: no network traffic to capture on this interface.")

def handle_exit(game, args):
    game.game_active = False

COMMAND_MAP = {
    'help': handle_help,
    'pwd': handle_pwd,
    'ls': handle_ls,
    'dir': handle_ls,
    'cd': handle_cd,
    'cat': handle_cat,
    'ssh': handle_ssh,
    'nmap': handle_nmap,
    'exit': handle_exit,
    'grep': handle_grep,
    'tcpdump': handle_tcpdump,
}
