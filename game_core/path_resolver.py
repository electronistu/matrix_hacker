class PathResolver:
    def __init__(self, game_instance):
        self.game = game_instance

    def get_current_path(self):
        path = []
        current = self.game.player.current_directory
        while current:
            path.append(current.name)
            current = current.parent
        if len(path) <= 1: return "/"
        else: return "/" + "/".join(reversed(path[:-1]))
