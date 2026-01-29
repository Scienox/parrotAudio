import sys
import os
import time
# On force le mode sans écran AVANT d'importer Qt
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput

def main():
    app = QCoreApplication(sys.argv)

    player = QMediaPlayer()
    audio_output = QAudioOutput()
    player.setAudioOutput(audio_output)

    # Chemin absolu vers ton fichier
    file_path = "/home/bexjo/Music/badromance.mp3"
    
    if not os.path.exists(file_path):
        print(f"ERREUR : Le fichier est introuvable ici : {file_path}")
        return

    player.setSource(QUrl.fromLocalFile(file_path))
    audio_output.setVolume(1.0) # Volume au max pour le test

    # On surveille l'état
    def status_changed(status):
        print(f"Statut : {status}")
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            print("Fichier chargé, lancement de la lecture...")
            player.play()
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            print("Fin du morceau.")
            app.quit()

    def error_occurred(error, error_str):
        print(f"ERREUR QT : {error_str}")
        app.quit()

    player.mediaStatusChanged.connect(status_changed)
    player.errorOccurred.connect(error_occurred)

    print("Démarrage de la boucle Qt...")
    # On force un play au cas où le signal Loaded arrive trop vite
    player.play() 
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()