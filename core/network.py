from core.filesystem import Directory

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
