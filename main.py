from modules.mp3 import Mp3
from modules.server import AudioServer


if __name__ == "__main__":
    running = True
    srv = AudioServer()
    srv.start()
    mp3 = Mp3()

    while running:
        if srv.last_message:
            print(f"Message intercepté: {srv.last_message}")
            srv.last_message = None  # Réinitialiser après traitement
