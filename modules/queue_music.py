from os import listdir
    
class NodeMusic:

    def __init__(self, typePath: str, path: str, title: str):
        self.typePath = typePath
        self.path = path
        self.title = title
        self.next = None
        self.prev = None

    def delete(self): 
        self.next = self.next.next
        self.next.prev = self.prev
    
    def __repr__(self):
        return f"NodeMusic(title='{self.title}')"


class QueueMusic:
    
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
    
    def _iter_queue(self):
        """Itère sur toutes les musiques de la playlist."""
        node = self.head
        for _ in range(self.size):
            yield node
            node = node.next

    def show_music_titles(self):
        value = "|".join(node.title for node in self._iter_queue())
        return value
    
    def found_files_from_folder(self, folder=None):
        if folder is None:
            folder = self.path_local_files
        files = listdir(folder)
        files = "|".join(f for f in files)
        return files

    def delete_this_index_in_queue(self, index):
        if self.size:
            if (0 <= index < self.size):
                for i, node in enumerate(self._iter_queue()):
                    if i == index:
                        if self.size == 1:
                            self.clear()
                        else:
                            node.delete()
                            self.size -= 1
    
    def clear(self):
        self.head = self.current = None
        self.size = 0
