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
