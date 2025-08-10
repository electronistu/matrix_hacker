import random
from core.filesystem import File, Directory
from core.network import Server
from campaign.lore import MISSION_FRAGMENTS, RKSE_FRAGMENTS

class CampaignGenerator:
    def __init__(self, game_instance):
        self.game = game_instance
        self.all_servers = {}
        self.ip_prefix = 10
        self.commands_to_learn = ['grep', 'find', 'tcpdump', 'portscan']

    def _get_next_ip_prefix(self):
        self.ip_prefix += 1
        return f"{self.ip_prefix}.{random.randint(1, 254)}.{random.randint(1, 254)}"

    def _create_server(self, ip, name, server_type='default'):
        pos_x = int(self.game.screen.get_width() * 0.8 + random.randint(-250, 250))
        pos_y = int(self.game.screen.get_height() / 2 + random.randint(-300, 300))
        server = Server(ip, name, server_type, (pos_x, pos_y))
        self.all_servers[ip] = server
        return server

    def generate_campaign(self, num_missions=5):
        # --- Home PC Setup ---
        home_pc = Server("127.0.0.1", "home-pc", position=(int(self.game.screen.get_width()*0.7), self.game.screen.get_height() // 2))
        home_pc.is_discovered = True
        home_pc.add_user('operative', '')
        home_pc.fs.get_child('bin').add_child(File("ssh.hlp", "COMMAND: ssh <user>@<ip>\nConnects to a remote server."))
        self.all_servers["127.0.0.1"] = home_pc

        # --- Work Server Setup ---
        work_serv_ip = "192.168.1.10"
        work_server = self._create_server(work_serv_ip, "work-serv", server_type="work_server")
        work_server.add_user('op_contract', 'password123')
        home_pc.fs.get_child('home').get_child('operative').add_child(File("chronosync_contract.txt", f"Welcome, Operative. Your work terminal is at IP: {work_serv_ip} (Description: Chronosync Workstation). Use credentials op_contract:password123. Your first mission brief is on the terminal."))
        home_pc.fs.get_child('home').get_child('operative').add_child(File("underground_markets.txt", "Found a lead on a black market...\nIP: 13.37.13.37 (Description: Black Market)\nUser: market"))

        # Add side jobs to the work server
        jobs_dir = Directory("jobs")
        work_server.fs.get_child('home').add_child(jobs_dir)
        jobs_dir.add_child(File("job1.txt", "Data Retrieval: Find the employee of the month for October from /var/corp_data/archives.log. Payment: 150 Creds."))
        
        archive_dir = Directory("archives")
        corp_data_dir = Directory("corp_data")
        work_server.fs.get_child('var').add_child(corp_data_dir)
        corp_data_dir.add_child(archive_dir)
        archive_dir.add_child(File("archives.log", "Employee of the Month (October): Sarah Jenkins"))

        # --- Black Market Server Setup ---
        market_ip = "13.37.13.37"
        market_server = self._create_server(market_ip, "black-market", server_type="black_market")
        market_server.add_user("market", "")
        market_server.fs.add_child(File("welcome.txt", "Welcome to the Black Market.\nUse 'list software' or 'list hardware' to see available items.\nUse 'buy <item_name>' to purchase."))

        # --- Generate Mission Chain ---
        next_mission_ip = "10.1.1.1"
        for i in range(num_missions):
            mission_brief = MISSION_FRAGMENTS[i % len(MISSION_FRAGMENTS)]
            lore_piece = RKSE_FRAGMENTS[i % len(RKSE_FRAGMENTS)]
            is_final_mission = (i == num_missions - 1)

            entry_ip, next_mission_ip = self._generate_mission_network(
                entry_ip=next_mission_ip, 
                mission_num=i + 1,
                mission_brief=mission_brief, 
                lore_piece=lore_piece, 
                is_final=is_final_mission
            )
            
            if i == 0:
                work_server.fs.get_child('home').add_child(Directory('op_contract'))
                work_server.fs.get_child('home').get_child('op_contract').add_child(File(f"mission_{i+1}.txt", f"{mission_brief}\nYour first target is the gateway at IP: {entry_ip} (Description: Chronosync Mission {i+1})."))

        return self.all_servers

    def _generate_mission_network(self, entry_ip, mission_num, mission_brief, lore_piece, is_final):
        mission_templates = [self._generate_grep_mission, self._generate_find_mission, self._generate_tcpdump_mission]
        if mission_num == 1:
            chosen_template = self._generate_grep_mission
        else:
            chosen_template = random.choice(mission_templates)
        return chosen_template(entry_ip, mission_num, mission_brief, lore_piece, is_final)

    def _place_learnable_command(self, server):
        if self.commands_to_learn:
            command_to_place = self.commands_to_learn.pop(0)
            server.fs.get_child('bin').add_child(File(f"{command_to_place}.hlp", f"COMMAND: {command_to_place}\nNew command available for purchase on the Black Market."))

    def _generate_grep_mission(self, entry_ip, mission_num, mission_brief, lore_piece, is_final):
        s1_ip = entry_ip
        s2_ip = f"{s1_ip.rsplit('.', 1)[0]}.{random.randint(1, 254)}"
        s3_ip = f"{s1_ip.rsplit('.', 1)[0]}.{random.randint(1, 254)}"
        next_mission_entry_ip = f"{self._get_next_ip_prefix()}.1"

        server1 = self._create_server(s1_ip, f"gw-node-{self.ip_prefix}", 'firewall')
        server2 = self._create_server(s2_ip, f"data-node-{self.ip_prefix}")
        server3 = self._create_server(s3_ip, f"archive-node-{self.ip_prefix}", 'data')

        server1.add_user('guest', 'guest')
        server2.add_user('user', 'password')
        server3.add_user('archivist', 'archive')

        server1.fs.get_child('home').get_child('guest').add_child(File("readme.txt", f"System access is logged in /var/logs/system.log. The data server is at IP: {s2_ip} (Description: Data Node)."))
        self._place_learnable_command(server1)

        log_content = "INFO: User 'guest' logged in.\n" * 10
        log_content += f"INFO: Credentials for {s2_ip} are user: user pass: password.\n"
        log_content += "ERROR: Failed login for user 'admin'.\n" * 5
        server1.fs.get_child('var').add_child(Directory('logs'))
        server1.fs.get_child('var').get_child('logs').add_child(File("system.log", log_content))

        server2.fs.get_child('home').get_child('user').add_child(File("notes.txt", f"The final archive is at IP: {s3_ip} (Description: Archive Node). The user is 'archivist'. I can never remember the password, but I wrote it down in a hidden file somewhere on this server."))
        server2.fs.add_child(File(".password_backup", f"pass: archive for IP: {s3_ip}"))

        server3.fs.get_child('home').get_child('archivist').add_child(File("payment.txt", "Chronosync transfer complete: 500 Creds."))
        server3.fs.get_child('home').get_child('archivist').add_child(File(lore_piece['title'], lore_piece['content']))
        if not is_final:
            next_mission_file_content = f"{mission_brief}\nYour next target is the gateway at IP: {next_mission_entry_ip} (Description: Chronosync Mission {mission_num + 1})."
            server3.fs.get_child('home').get_child('archivist').add_child(File(f"mission_{mission_num + 1}.txt", next_mission_file_content))
        else:
            server3.fs.get_child('home').get_child('archivist').add_child(File("FINAL_entry.txt", "You have all the fragments. The truth is in your hands now, operative."))

        
        return entry_ip, next_mission_entry_ip

    def _generate_find_mission(self, entry_ip, mission_num, mission_brief, lore_piece, is_final):
        s1_ip = entry_ip
        s2_ip = f"{s1_ip.rsplit('.', 1)[0]}.{random.randint(1, 254)}"
        next_mission_entry_ip = f"{self._get_next_ip_prefix()}.1"

        server1 = self._create_server(s1_ip, f"clutter-node-{self.ip_prefix}")
        server2 = self._create_server(s2_ip, f"archive-node-{self.ip_prefix}", 'data')
        server1.add_user('guest', 'guest')
        server2.add_user('archivist', 'archive')

        server1.fs.get_child('home').get_child('guest').add_child(File("readme.txt", f"This server is a mess. The data we need is on the archive server (IP: {s2_ip} (Description: Archive Node)), but the password is in a file named 'config.bak' somewhere on this machine. Use 'find' to locate it."))
        self._place_learnable_command(server1)

        dummy_dirs = [server1.fs.get_child('home')]
        for i in range(10):
            d = Directory(f"dir_{i}")
            random.choice(dummy_dirs).add_child(d)
            if random.random() > 0.5:
                dummy_dirs.append(d)
            d.add_child(File("file.txt", "empty"))
        random.choice(dummy_dirs).add_child(File("config.bak", f"pass: archive for IP: {s2_ip}"))

        server2.fs.get_child('home').get_child('archivist').add_child(File("payment.txt", "Chronosync transfer complete: 300 Creds."))
        server2.fs.get_child('home').get_child('archivist').add_child(File(lore_piece['title'], lore_piece['content']))
        if not is_final:
            server2.fs.get_child('home').get_child('archivist').add_child(File(f"mission_{mission_num + 1}.txt", f"{mission_brief}\nYour next target is IP: {next_mission_entry_ip} (Description: Chronosync Mission {mission_num + 1})."))
        else:
            server2.fs.get_child('home').get_child('archivist').add_child(File("FINAL_entry.txt", "You have all the fragments."))

        return entry_ip, next_mission_entry_ip

    def _generate_tcpdump_mission(self, entry_ip, mission_num, mission_brief, lore_piece, is_final):
        s1_ip = entry_ip
        next_mission_entry_ip = f"{self._get_next_ip_prefix()}.1"

        server1 = self._create_server(s1_ip, f"comm-hub-{self.ip_prefix}")
        server1.add_user('guest', 'guest')

        server1.fs.get_child('home').get_child('guest').add_child(File("readme.txt", "This server handles unencrypted traffic. The password for the next mission's server is probably flying around here somewhere. Use 'tcpdump' to capture it."))
        self._place_learnable_command(server1)

        capture_content = "...noise...\n" * 5
        capture_content += f"SSH_AUTH - IP: {next_mission_entry_ip} (Description: Chronosync Mission {mission_num + 1}) user: admin pass: mission_{mission_num + 1}_pass\n"
        capture_content += "...noise...\n" * 5
        server1.fs.add_child(File(".tcp_capture", capture_content))

        server1.fs.get_child('home').get_child('guest').add_child(File("payment.txt", "Chronosync transfer complete: 400 Creds."))
        server1.fs.get_child('home').get_child('guest').add_child(File(lore_piece['title'], lore_piece['content']))
        if not is_final:
            server1.fs.get_child('home').get_child('guest').add_child(File(f"mission_{mission_num + 1}.txt", f"{mission_brief}\nYour next target is IP: {next_mission_entry_ip} (Description: Chronosync Mission {mission_num + 1})."))
        else:
            server1.fs.get_child('home').get_child('guest').add_child(File("FINAL_entry.txt", "You have all the fragments."))

        return entry_ip, next_mission_entry_ip
