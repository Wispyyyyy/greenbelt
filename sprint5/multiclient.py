import socket
import threading
import datetime

class ChatClient:
    def __init__(self, host="10.10.25.109", port=8000):
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.nickname = ""
        self.running = False
        self.closed = False
    
    def write_log(self, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open("server_log.txt", "a") as log_file:
            log_file.write(f"{timestamp} - {message}\n")

    def connect(self):
        try:
            self.client_socket.connect((self.host, self.port))
            
            self.nickname = input("Choose your nickname: ").strip()

            if self.nickname == "":
                self.nickname = "Guest"

            self.client_socket.sendall(self.nickname.encode("utf-8"))

            self.running = True

        except ConnectionRefusedError:
            print("Could not connect. Make sure the server is running first.")

    def recieve_messages(self):
        while self.running:
            try:
                message = self.client_socket.recv(1024).decode("utf-8")

                if message == "":
                    break

                print(f"\n{message}")
                self.write_log(message)

            except ConnectionResetError:
                break

            except OSError:
                break

        self.running = False
    

    def write_messages(self):
        while self.running:
            try:
                message = input("Enter message or type 'exit': ")

                if message.lower() == "exit":
                    self.client_socket.sendall("exit".encode("utf-8"))

                    self.write_log(f"{self.nickname} left the chat.")
                    break

                if message.strip() != "":
                    self.client_socket.sendall(message.encode("utf-8"))

                    self.write_log(f"{self.nickname}: {message}")

            except OSError:
                print("The message could not be sent.")
                break
        self.running = False

    def close(self):
        if self.closed:
            return
        
        self.closed = True
        self.running = False

        try:
            self.client_socket.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass

        try:
            self.client_socket.close()
        except OSError:
            pass

        print("Client closed.")

    def run(self):
        self.connect()

        if not self.running:
            return
        
        recieve_thread = threading.Thread(target=self.recieve_messages)
        write_thread = threading.Thread(target=self.write_messages)

        recieve_thread.start()
        write_thread.start()

        write_thread.join()

        self.close()

        recieve_thread.join()

if __name__ == "__main__":
    chat_client = ChatClient()
    chat_client.run()