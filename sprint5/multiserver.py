import socket
import threading
import datetime

class ChatServer:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.nicknames = {} 
        self.lock = threading.Lock()


    def write_log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("server_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} - {message}\n")


    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        start_message = f"Server is listening on {self.host}:{self.port}"

        print(start_message)
        self.write_log(start_message)

    def broadcast(self, message, sender_client=None):
        with self.lock:
            clients_copy = self.clients.copy()

            for client in clients_copy:
                if client != sender_client:
                    try:
                        client.sendall(message.encode("utf-8"))
                    except OSError:
                        self.remove_client(client)
    def remove_client(self, client):
        nickname = None

        with self.lock:
            if client in self.clients:
                self.clients.remove(client)

            nickname = self.nicknames.pop(client, None)

            try:
                client.close()
            except OSError:
                pass

            if nickname is not None:
                leave_message = f"{nickname} got kicked :(. "
                
                print(leave_message)
                self.write_log(leave_message)
                self.broadcast(leave_message)

    def handle_client(self, client):
        nickname = self.nicknames.get(client, "Unknown")

        while True:
            try:
                message = client.recv(1024).decode("utf-8")

                if message == "":
                    break

                if message.lower() == "exit":
                    break

                full_message = f"{nickname}: {message}"
                print(full_message)
                self.write_log(full_message)


                self.broadcast(full_message, client)

            except ConnectionResetError:
                break

            except OSError:
                break

        self.remove_client(client)

    def recieve_connections(self):
        while True:
            try:
                client, address = self.server_socket.accept()

                nickname = client.recv(1024).decode("utf-8").strip()

                if nickname == "":
                    client.close()
                    continue

                with self.lock:
                    self.clients.append(client)
                    self.nicknames[client] = nickname

                connect_message = f"{nickname} connected from {address}"

                print(connect_message)
                self.write_log(connect_message)

                client.sendall("Connected to the server!".encode("utf-8"))

                self.broadcast(f"{nickname} joined the chat.", client)

                client_thread = threading.Thread(
                    target = self.handle_client, args=(client,), daemon=True
                )

                client_thread.start()

            except OSError:
                break
        
    def close_server(self):
        print("\nClosing server...")

        with self.lock:
            clients_copy  = self.clients.copy()
            self.clients.clear()
            self.nicknames.clear()

        for client in clients_copy:
            try:
                client.close()
            except OSError:
                pass

        try:
            self.server_socket.close()
        except OSError:
            pass
        self.write_log("Server closed.")
        print("Server closed.")

    def run(self):
        try:
            self.start()
            self.recieve_connections()

        except KeyboardInterrupt:
            print("\nServer stopped by the user.")

        finally:
            self.close_server()

if __name__ == "__main__":
    chat_server = ChatServer()
    chat_server.run()