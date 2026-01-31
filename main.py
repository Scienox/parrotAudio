import vlc
import time
import os


class Mp3:    
    def __init__(self, file_path):
        self.file_path = file_path
        self.instance = None
        self.player = None
        self.media = None
        self._validate_file()
    
    def _validate_file(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Le fichier {self.file_path} est introuvable.")
    
    def _init_vlc(self):
        if self.instance is None:
            self.instance = vlc.Instance('--intf dummy --no-video --quiet')
            self.player = self.instance.media_player_new()
    
    def play(self):
        self._init_vlc()
        
        self.media = self.instance.media_new(self.file_path)
        self.player.set_media(self.media)
        
        print(f"Lecture en cours : {self.file_path}")
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


if __name__ == "__main__":
    try:
        mon_fichier = "/home/bexjo/Music/badromance.mp3"
        lecteur = Mp3(mon_fichier)
        lecteur.play()
    except FileNotFoundError as e:
        print(f"Erreur : {e}")
        