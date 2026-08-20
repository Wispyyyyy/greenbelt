import socket

class Server:
    def __init__ (self, host = '127.0.0.1', port = 12345):
        self.host = host
        self.port = port
        self.messages = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("Server listening on port", self.port)

    def get_connection(self):
        client_socket, addr = self.server_socket.accept()
        print("Got a connection from", addr)
        return client_socket, addr
    
    def recieve(self, client_socket):
        try:
            return client_socket.recv(1024).decode()
        except socket.error as e:
            print(f'Error: {e}')

    def send(self, client_socket, message):
        client_socket.sendall(message.encode())

    def run(self):
        self.start()
        client_socket, client_address = self.get_connection()

        while True:
            message = self.recieve(client_socket)

            if message == "":
                print("Client disconnected.")
                break

            if message.lower() == "exit":
                print("Client ended the chat.")
                break

            self.messages.append(message)
            print(f"Recieved from {client_address}: {message}")

            response = f"Server recieved: {message}"

            self.send(client_socket, response)

        client_socket.close()
        self.server_socket.close()
        print("Server closed.")

server = Server()

server.run()

            

