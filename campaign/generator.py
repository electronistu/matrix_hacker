import random
from core.filesystem import File, Directory
from core.network import Server
from campaign.lore import MISSION_FRAGMENTS, RKSE_FRAGMENTS

class CampaignGenerator:
    def __init__(self, game_instance):
        self.game = game_instance
        self.all_servers = {}
        self.ip_prefix = 10

    def _get_next_ip_prefix(self):
        self.ip_prefix += 1
        return f"{self.ip_prefix}.{random.randint(1, 254)}"

    def _create_server(self, ip, name, server_type='default'):
        pos_x = int(self.game.screen.get_width() * 0.8 + random.randint(-250, 250))
        pos_y = int(self.game.screen.get_height() / 2 + random.randint(-300, 300))
        server = Server(ip, name, server_type, (pos_x, pos_y))
        self.all_servers[ip] = server
        return server

    def generate_campaign(self, num_missions=5):
        # --- Local Server Setup ---
        local_server = Server("127.0.0.1", "local-node", position=(int(self.game.screen.get_width()*0.8), self.game.screen.get_height() // 2))
        local_server.is_discovered = True
        local_server.add_user('operative', '')
        local_server.fs.get_child('bin').add_child(File("ssh.hlp", "COMMAND: ssh <user>@<ip>\nConnects to a remote server."))
        self.all_servers["127.0.0.1"] = local_server

        # --- Generate Mission Chain ---
        next_mission_ip = "10.1.1.1"
        for i in range(num_missions):
            mission_brief = random.choice(MISSION_FRAGMENTS)
            lore_piece = RKSE_FRAGMENTS[i % len(RKSE_FRAGMENTS)]
            
            # The last mission has a different goal
            is_final_mission = (i == num_missions - 1)

            # Generate a mission and get the IP for the *next* one
            entry_ip, next_mission_ip = self._generate_mission_network(next_mission_ip, mission_brief, lore_piece, is_final_mission)
            
            if i == 0:
                local_server.fs.get_child('home').get_child('operative').add_child(File(f"mission_{i+1}.txt", f"{mission_brief}\nYour first target is the gateway at {entry_ip}."))

        return self.all_servers

    def _generate_mission_network(self, entry_ip, mission_brief, lore_piece, is_final):
        # --- Create Servers ---
        s1_ip = entry_ip
        s2_ip = f"{s1_ip.rsplit('.', 1)[0]}.{random.randint(1, 254)}"
        s3_ip = f"{s1_ip.rsplit('.', 1)[0]}.{random.randint(1, 254)}"
        next_mission_entry_ip = f"{self._get_next_ip_prefix()}.1"

        server1 = self._create_server(s1_ip, f"gw-node-{self.ip_prefix}", 'firewall')
        server2 = self._create_server(s2_ip, f"data-node-{self.ip_prefix}")
        server3 = self._create_server(s3_ip, f"archive-node-{self.ip_prefix}", 'data')

        # --- Create Users & Clues ---
        server1.add_user('guest', 'guest')
        server2.add_user('user', 'password')
        server3.add_user('archivist', 'archive')

        # --- Place Clues (This is a simple grep mission template) ---
        server1.fs.get_child('home').get_child('guest').add_child(File("readme.txt", f"System access is logged in /var/logs/system.log. The data server is at {s2_ip}."))
        server1.fs.get_child('bin').add_child(File("grep.hlp", "COMMAND: grep <pattern> <file>\nSearches for a pattern in a file."))

        log_content = "INFO: User 'guest' logged in.\n" * 10
        log_content += "INFO: User 'user' logged in with password 'password'.\n"
        log_content += "ERROR: Failed login for user 'admin'.\n" * 5
        server1.fs.get_child('var').add_child(Directory('logs'))
        server1.fs.get_child('var').get_child('logs').add_child(File("system.log", log_content))

        server2.fs.get_child('home').get_child('user').add_child(File("notes.txt", f"The final archive is at {s3_ip}. The user is 'archivist'. I can never remember the password, but I wrote it down in a hidden file somewhere on this server."))
        server2.fs.add_child(File(".password_backup", "archive"))

        # --- Place Lore & Next Mission Clue ---
        server3.fs.get_child('home').get_child('archivist').add_child(File(lore_piece['title'], lore_piece['content']))
        if not is_final:
            server3.fs.get_child('home').get_child('archivist').add_child(File("next_target.txt", f"Mission complete. The next data fragment is located at {next_mission_entry_ip}"))
        else:
            server3.fs.get_child('home').get_child('archivist').add_child(File("FINAL_entry.txt", "You have all the fragments. The truth is in your hands now, operative."))

        return entry_ip, next_mission_entry_ip