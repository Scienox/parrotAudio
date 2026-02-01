import vlc
import time
import os
import threading
from .playlist import Playlist


class Mp3:
    def __init__(self):
        self.playlist = Playlist()
        self.instance = None
        self.player = None
        self.media = None
        self.music_folder = "/home/bexjo/Music/"
        self.on_music_end = self.play

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
        song = self.playlist.get_current()
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
        self.current = self.playlist.next_music()
    
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
    
    def get_duration(self):
        self._init_vlc()
        song = self.playlist.get_current()
        if not song: return 0
        media = self.instance.media_new(song.path)
        media.parse()
        return media.get_duration()
    
    def handle_command(self, message: dict, server):
        """Traite une commande reçue et répond."""
        cmd = message['message'].lower()
        
        try:
            doubleCmd = True if ':' in cmd else False
            if doubleCmd:
                cmd, value = cmd.split(':', 1)
                if cmd == 'add':
                    if os.path.isfile(self.music_folder + value):
                        title = value.split('/')[-1].split('.')[0]
                        self.playlist.add_local(value, title=title)
                        server.send_response(message, f"Musique ajoutée: {value}")
                    else:
                        server.send_response(message, f"Erreur: Fichier introuvable: {value}")
                elif cmd == "show":
                    if value == "playlist":
                        titles = self.playlist.show_music_titles()
                        response = "Playlist:\n" + "\n".join(titles)
                        server.send_response(message, response)
                    elif value == "files":
                        files = self.playlist.found_files_from_folder()
                        response = "Fichiers musicaux:\n" + files
                        server.send_response(message, response)
                    else:
                        server.send_response(message, "Erreur: Commande show inconnue")
                else:
                    server.send_response(message, "Erreur: Commande inconnue")

            elif cmd == 'play':
                # Lancer la musique en arrière-plan
                thread = threading.Thread(target=self.play, daemon=True)
                thread.start()
                server.send_response(message, f"{self.playlist.get_current().title} en lecture")
            elif cmd == 'next':
                self.next()
                server.send_response(message, f"Passage à : {self.playlist.get_current().title}")
            elif cmd == 'pause':
                self.pause()
                server.send_response(message, "Lecture en pause")
            elif cmd == 'resume':
                self.resume()
                server.send_response(message, "Lecture reprise")
            else:
                server.send_response(message, "Erreur: Commande inconnue")
        except Exception as e:
            server.send_response(message, f"Erreur: {e}")