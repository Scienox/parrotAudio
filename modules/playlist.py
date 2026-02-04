from os import listdir

class NodeMusic:
    
    def __init__(self, typePath: str, path: str, title: str):
        self.typePath = typePath
        self.path = path
        self.title = title
        self.next = None
        self.prev = None
    
    def __repr__(self):
        return f"NodeMusic(title='{self.title}')"


class Playlist:
    
    def __init__(self):
        self.path_local_files = "/home/bexjo/Music/"
        self.head = None
        self.tail = None
        self.current = None
        self.size = 0
    
    def __add(self, typePath: str, path: str, title: str = None):
        node = NodeMusic(typePath, path, title)
        
        if self.head is None:
            # Première musique
            self.head = self.head.next = self.head.prev = self.tail = node
            self.current = node
        else:
            # Ajouter à la fin
            self.tail.next = node
            node.prev = self.tail
            self.tail = node
            self.head.prev = self.tail
            self.tail.next = self.head
        
        self.size += 1

    def add_local(self, file: str, title: str = None):
        self.__add("local", f"{self.path_local_files}{file}", title)

    def add_url(self, url: str, title: str = None):
        self.__add("url", url, title)
        
    
    def next_music(self):
        """Passe à la musique suivante."""
        if self.current and self.current.next:
            self.current = self.current.next
            return self.current
        return None
    
    def prev_music(self):
        """Revient à la musique précédente."""
        if self.current and self.current.prev:
            self.current = self.current.prev
            return self.current
        return None
    
    def get_current(self):
        return self.current
    
    def _iterate_playlist(self):
        """Itère sur toutes les musiques de la playlist."""
        node = self.head
        for _ in range(self.size):
            yield node
            node = node.next

    def show_music_titles(self):
        value = ""
        for node in self._iterate_playlist():
            value += f"{node.title}\n"
        return value
    
    def found_files_from_folder(self, folder=None):
        if folder is None:
            folder = self.path_local_files
        files = listdir(folder)
        files = "|".join(f for f in files)
        return files
    
    def clear(self):
        self.head = self.current = None
        self.size = 0
