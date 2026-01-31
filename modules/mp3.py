import vlc
import time
import os
from .playlist import Playlist


class Mp3:
    def __init__(self):
        self.playlist = Playlist()
        self.instance = None
        self.player = None
        self.media = None

    def _init_vlc(self):
        if self.instance is None:
            self.instance = vlc.Instance('--intf dummy --no-video --quiet')
            self.player = self.instance.media_player_new()
    
    def play(self):
        self._init_vlc()
        song = self.playlist.get_current()
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
        media = self.instance.media_new(self.file_path)
        media.parse()
        return media.get_duration()