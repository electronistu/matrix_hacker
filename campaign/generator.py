import random
from core.filesystem import File, Directory
from core.network import Server
from campaign.lore import MISSION_FRAGMENTS, RKSE_FRAGMENTS

class CampaignGenerator:
    def __init__(self, game_instance):
        self.game = game_instance
        self.servers = {}

    def _create_base_server(self, ip, name, pos):
        server = Server(ip, name, position=pos)
        # The /bin directory is empty by default.
        # Missions will populate it with .hlp files for learnable commands.
        return server

    def generate_mission_one(self):
        # --- Local Server Setup ---
        local_server = Server("127.0.0.1", "local-node", position=(int(self.game.screen.get_width()*0.8), self.game.screen.get_height() // 2))
        local_server.is_discovered = True
        local_server.add_user('operative', '')
        local_server.fs.get_child('bin').add_child(File("ssh.hlp", "COMMAND: ssh <user>@<ip>\nConnects to a remote server."))
        self.servers["127.0.0.1"] = local_server

        # --- Network Setup ---
        gw_ip = "10.1.1.1"
        db_ip = "10.1.1.2"
        
        gateway_server = self._create_base_server(gw_ip, "corp-gateway", (int(self.game.screen.get_width()*0.7), self.game.screen.get_height() // 3))
        database_server = self._create_base_server(db_ip, "archive-db", (int(self.game.screen.get_width()*0.9), self.game.screen.get_height() // 2))
        
        self.servers[gw_ip] = gateway_server
        self.servers[db_ip] = database_server

        # --- Clue Placement ---
        local_server.fs.get_child('home').get_child('operative').add_child(File("mission.txt", f"Your first mission is to access the corporate gateway at {gw_ip}. Find a file containing employee credentials."))

        gateway_server.add_user('guest', 'guest')
        gateway_server.fs.get_child('home').get_child('guest').add_child(File("readme.txt", "Access to this server is restricted. All activity is logged in /var/logs/auth.log"))
        
        log_content = "INFO: User 'guest' logged in.\n" * 5
        log_content += "INFO: User 'admin' logged in.\n"
        log_content += "ERROR: Failed login for user 'j.smith'.\n" * 3
        log_content += f"INFO: Credentials for db server {db_ip} are user: 'archive' pass: 'S3cretP@ss'.\n"
        log_content += "ERROR: System rebooting.\n"
        gateway_server.fs.get_child('var').add_child(Directory('logs'))
        gateway_server.fs.get_child('var').get_child('logs').add_child(File("auth.log", log_content))
        gateway_server.fs.get_child('bin').add_child(File("grep.hlp", "COMMAND: grep <pattern> <file>\nSearches for a pattern within a file."))

        database_server.add_user('archive', 'S3cretP@ss')
        lore_piece = random.choice(RKSE_FRAGMENTS)
        database_server.fs.get_child('home').get_child('archive').add_child(File(lore_piece['title'], lore_piece['content']))
        database_server.fs.get_child('home').get_child('archive').add_child(File("next_mission.txt", "Mission complete. The next data fragment is located at 10.2.2.1"))

        return self.servers
