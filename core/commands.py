import re
import time

# Import handlers from new command files
from commands.general import handle_help, handle_pwd, handle_ls, handle_cd, handle_cat, handle_exit
from commands.network import handle_nmap, handle_ssh, handle_grep, handle_tcpdump, handle_find, handle_portscan
from commands.quest import handle_deliver, handle_list_quests, handle_accept_quest, handle_ping

# HELP_MESSAGES is now defined in commands/general.py, but we can keep a reference here if needed for other modules
# For now, we'll assume it's accessed directly from general.py if needed elsewhere.

COMMAND_MAP = {
    'help': handle_help,
    'pwd': handle_pwd,
    'ls': handle_ls,
    'dir': handle_ls, # Alias
    'cd': handle_cd,
    'cat': handle_cat,
    'ssh': handle_ssh,
    'nmap': handle_nmap,
    'exit': handle_exit,
    'grep': handle_grep,
    'tcpdump': handle_tcpdump,
    'find': handle_find,
    'portscan': handle_portscan,
    'deliver': handle_deliver,
    'list': handle_list_quests,
    'accept': handle_accept_quest,
    'ping': handle_ping,
}