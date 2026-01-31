import socket
import threading
import queue


class AudioServer:
    """Serveur simple qui stocke les messages dans une queue thread-safe.

    Utiliser `get_message(block=True, timeout=None)` pour récupérer
    le prochain message sans faire de busy-waiting.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.thread = None
        self._queue: "queue.Queue[dict]" = queue.Queue()

    def _handle_client(self, client_socket, address):
        try:
            data = client_socket.recv(4096).decode('utf-8').strip()
            if data:
                msg = {
                    'message': data,
                    'ip': address[0],
                    'port': address[1],
                    'socket': client_socket  # garder la référence au socket
                }
                # place le message dans la queue (thread-safe)
                self._queue.put(msg)
                # NE PAS fermer le socket ici — il sera utilisé pour répondre
        except Exception as e:
            print(f"Erreur: {e}")
            try:
                client_socket.close()
            except Exception:
                pass

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.running = True

        print(f"🎵 Serveur écoute sur {self.host}:{self.port}")

        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _listen_loop(self):
        try:
            while self.running:
                client_socket, address = self.server_socket.accept()
                threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, address),
                    daemon=True,
                ).start()
        except OSError:
            pass

    def get_message(self, block: bool = True, timeout: float = None) -> dict | None:
        """Récupère le prochain message.

        Args:
            block: si True, bloque jusqu'à ce qu'un message soit disponible
            timeout: délai d'attente (secondes) si block=True

        Returns:
            dict: {'message', 'ip', 'port', 'socket'} ou None si aucun message
        """
        try:
            return self._queue.get(block=block, timeout=timeout)
        except queue.Empty:
            return None

    def send_response(self, message: dict, response: str | bytes):
        """Envoie une réponse au client.

        Args:
            message: dict reçu de get_message()
            response: str ou bytes à envoyer
        """
        try:
            if isinstance(response, str):
                response = response.encode('utf-8')
            message['socket'].send(response)
        except Exception as e:
            print(f"Erreur d'envoi au client {message['ip']}: {e}")
        finally:
            try:
                message['socket'].close()
            except Exception:
                pass

    def stop(self):
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except Exception:
                pass



