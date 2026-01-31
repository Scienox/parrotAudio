import socket
import threading


class AudioServer:
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        self.host = host
        self.port = port
        self.server_socket = None
        self.running = False
        self.thread = None
        self.last_message = None
    
    def _handle_client(self, client_socket, address):
        try:
            data = client_socket.recv(1024).decode('utf-8').strip()
            if data:
                self.last_message = data
                print(f"📨 [{address[0]}:{address[1]}] {data}")
                client_socket.send(b"OK")
        except Exception as e:
            print(f"Erreur: {e}")
        finally:
            client_socket.close()
    
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
                threading.Thread(target=self._handle_client, args=(client_socket, address), daemon=True).start()
        except OSError:
            pass
    
    def stop(self):
        self.running = False
        if self.server_socket:
            self.server_socket.close()



