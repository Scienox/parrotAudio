from modules.mp3 import Mp3
from modules.server import AudioServer


if __name__ == "__main__":
    srv = AudioServer()
    srv.start()
    mp3 = Mp3()

    print("Serveur lancé — attente des messages...")
    try:
        while True:
            msg = srv.get_message(block=True)
            if msg:
                # Passer le message au Mp3 pour traitement
                mp3.handle_command(msg, srv)
    except KeyboardInterrupt:
        print("\nArrêt demandé")
    finally:
        srv.stop()
