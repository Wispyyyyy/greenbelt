import socket

class Client:
    def __init__ (self, host = '127.0.0.1', port = 12345):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def connectMethod(self):
        self.client_socket.connect((self.host, self.port))
        print("Connected to server.")
    def send_message(self, message):
        self.client_socket.sendall(message.encode())
    def recieve_message(self):
        return self.client_socket.recv(1024).decode()
    
    def run(self):
        self.connectMethod()

        while True:
            message = input("Enter message ('exit' to quit): ")
            self.send_message(message)

            if message.lower() == "exit":
                break

            response = self.recieve_message()
            print("Recieved" + response)

        self.client_socket.close()
        print("Client closed.")

client = Client()

client.run()



