from modules.mp3 import Mp3

if __name__ == "__main__":
    running = True
    while running:
        mon_fichier = "/home/bexjo/Music/badromance.mp3"
        player = Mp3()
        player.playlist.add("localPath", mon_fichier, "Bad Romance")
        player.play()