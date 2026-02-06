import vlc
import time
import os
import threading
from .queue_music import QueueMusic


class Mp3:
    def __init__(self):
        self.queue = QueueMusic()
        self.instance = None
        self.player = None
        self.media = None
        self.music_folder = os.environ['HOME'] + "/Music/"
        self.playlist_folder = os.environ['HOME'] + "/Playlist/"
        self.on_music_end = self.play
        self.status = {"Is playing": self.is_playing,
        "Local files": self.queue.found_files_from_folder,
        }
        self._init_vlc()

    def _init_vlc(self):
        if self.instance is None:
            self.instance = vlc.Instance('--intf dummy --no-video --quiet')
            self.player = self.instance.media_player_new()
            self.event_manager = self.player.event_manager()
            self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self._on_music_end)

    def _on_music_end(self, event):
        """Déclenché par VLC quand une piste se termine."""
        if self.on_music_end:
            # On exécute le callback dans un thread pour ne pas bloquer VLC
            self.next()
            threading.Thread(target=self.on_music_end, daemon=True).start()
    
    def __play(self):
        self._init_vlc()
        song = self.queue.get_current()
        if not song:
            return

        self.media = self.instance.media_new(song.path)
        self.player.set_media(self.media)
        
        print(f"Lecture en cours : {song.title}")
        self.player.play()
        
        time.sleep(1)
        
        try:
            while self.player.is_playing():
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nArrêt de la lecture par l'utilisateur.")
            self.stop()
    
    def play(self):
        threading.Thread(target=self.__play, daemon=True).start()

    def next(self):
        self.current = self.queue.next_music()
    
    def stop(self):
        if self.player:
            self.player.stop()
            print("Lecture arrêtée.")
    
    def pause(self):
        if self.player:
            self.player.set_pause(True)
            print("Lecture mise en pause.")
    
    def resume(self):
        if self.player:
            self.player.set_pause(False)
            print("Lecture reprise.")
    
    def set_volume(self, volume):
        if self.player:
            if 0 <= volume <= 100:
                self.player.audio_set_volume(volume)
                print(f"Volume défini à {volume}%")
            else:
                print("Le volume doit être entre 0 et 100.")

    def get_playlists(self):
        return "|".join(file for file in os.listdir(self.playlist_folder))

    def read_playlist(self, playlist_name):
        with open(os.path.join(self.playlist_folder, playlist_name), "r") as file:
            lines = file.read().splitlines()
            logic_queue = QueueMusic()
            for line in lines:
                id_title, media_type, path_title, title = line.split(":")
                if media_type == "local":
                    logic_queue.add_local(path_title, title)
                elif media_type == "url":
                    continue
            file.close()
            return logic_queue

    def set_playlist(self, playlist_name):
        if playlist_name in self.get_playlists():
            self.queue = self.read_playlist(playlist_name)

    def get_duration(self):
        self._init_vlc()
        song = self.queue.get_current()
        if not song: return 0
        media = self.instance.media_new(song.path)
        media.parse()
        return media.get_duration()

    def get_status(self):
        value = ""
        for key, val in self.status.items():
            value += f"{key}:{str(val())}\n"
        return value

    def is_playing(self):
        return self.player.is_playing()
    
    def handle_command(self, message: dict, server):
        """Traite une commande reçue et répond."""
        cmd = message['message'].lower()
        
        try:
            doubleCmd = True if (1 < len(cmd.split(':')) < 3) else False
            tripleCmd = True if ':' in cmd and ':' in cmd.split(':')[1] else False
            if tripleCmd and doubleCmd:
                doubleCmd = False
            if doubleCmd:
                cmd, value = cmd.split(':', 1)
                if cmd == 'add':
                    if os.path.isfile(self.music_folder + value):
                        title = value.split('/')[-1].split('.')[0]
                        self.queue.add_local(value, title=title)
                        server.send_response(message, f"Musique ajoutée: {value}")
                    else:
                        server.send_response(message, f"Erreur: Fichier introuvable: {value}")
                elif cmd == "show":
                    if value == "queue":
                        titles = self.queue.show_music_titles()
                        response = f"Queue:\n{titles}"
                        server.send_response(message, response)
                    elif value == "files":
                        files = self.queue.found_files_from_folder()
                        response = "Fichiers musicaux:\n" + files
                        server.send_response(message, response)
                    else:
                        server.send_response(message, "Erreur: Commande show inconnue")
                else:
                    server.send_response(message, "Erreur: Commande inconnue")
            
            elif tripleCmd:
                cmd, value1, value2 = tripleCmd.split(":")
                if cmd == "set":
                    if value1 == "playlist":
                        self.stop()
                        self.set_playlist(value2)
                        server.send_response(message, f"Playlist définie: {value2}")

            elif cmd == 'get_status':
                server.send_response(message, self.get_status())

            elif cmd == 'play':
                # Lancer la musique en arrière-plan
                thread = threading.Thread(target=self.play, daemon=True)
                thread.start()
                server.send_response(message, f"{self.queue.get_current().title} en lecture")
            elif cmd == 'next':
                self.next()
                server.send_response(message, f"Passage à : {self.queue.get_current().title}")
            elif cmd == 'pause':
                self.pause()
                server.send_response(message, "Lecture en pause")
            elif cmd == 'stop':
                self.stop()
                server.send_response(message, "Lecture arrêtée")
            elif cmd == 'resume':
                self.resume()
                server.send_response(message, "Lecture reprise")
            else:
                server.send_response(message, "Erreur: Commande inconnue")
        except Exception as e:
            server.send_response(message, f"Erreur: {e}")
            