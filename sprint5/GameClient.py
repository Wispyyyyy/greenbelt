# GameClient.py
# This file lets one player connect and send game commands.

import json
import socket
import threading


def send_json(connection, data):
    # The newline matches the server's line-by-line reader. Without framing,
    # two quick commands could be received as one unreadable JSON value.
    message = json.dumps(data) + "\n"
    connection.sendall(message.encode("utf-8"))


class PlayerClient:
    def __init__(self, host="10.1.10.31", port=12345):
        self.host = host
        self.port = port

        self.client_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self.running = False

    @staticmethod
    def get_number(prompt):
        while True:
            try:
                number = int(input(prompt))

                if number < 1 or number > 10:
                    print("Enter a number from 1 to 10.")
                    continue

                return number

            except ValueError:
                print("Enter a whole number.")

    @staticmethod
    def get_player_stats():
        name = input(
            "Enter your character's name: "
        ).strip()

        print("Choose a character class:")
        print("1. Warrior")
        print("2. Wizard")
        print("3. IceWizard")

        class_choice = input("> ").strip()

        if class_choice == "1":
            character_class = "Warrior"
        elif class_choice == "3":
            character_class = "IceWizard"
        else:
            character_class = "Wizard"

        strength = PlayerClient.get_number(
            "Enter strength from 1 to 10: "
        )

        intelligence = PlayerClient.get_number(
            "Enter intelligence from 1 to 10: "
        )

        return {
            "type": "join",
            "name": name,
            "character_class": character_class,
            "strength": strength,
            "intelligence": intelligence,
        }

    def connect(self):
        try:
            self.client_socket.connect(
                (self.host, self.port)
            )

            player_stats = self.get_player_stats()
            send_json(self.client_socket, player_stats)

            self.running = True
            return True

        except ConnectionRefusedError:
            print(
                "Could not connect. Make sure the server "
                "is running first."
            )
            return False

        except OSError as error:
            print(f"Connection error: {error}")
            return False

    def display_data(self, packet):
        # The receiver thread converts packets into human-readable output;
        # keeping display rules here prevents game logic from leaking into the
        # keyboard input loop.
        packet_type = packet.get("type")
        data = packet.get("data")

        if data is None:
            return

        if packet_type == "players":
            for player in data:
                print(
                    f"- {player['name']} "
                    f"({player['character_class']}) "
                    f"Health: {player['health']} "
                    f"Position: {tuple(player['position'])}"
                )

        elif packet_type in {
            "status",
            "movement",
            "inventory",
        }:
            if "character_class" in data:
                print(f"Class: {data['character_class']}")
                print(f"Health: {data['health']}")
                print(f"Position: {tuple(data['position'])}")
                print(f"Skills: {data['skills']}")
                print(f"Inventory: {data['inventory']}")
            else:
                # Status packets can also describe the Goblin during the
                # optional inspect command, so display its smaller model.
                print(f"Name: {data['name']}")
                print(f"Health: {data['health']}")
                print(f"Position: {tuple(data['position'])}")

        elif packet_type == "scene":
            print(f"Scene: {data['name']}")
            print(f"Size: {data['size']}")
            print(f"NPCs: {data['npcs']}")
            print(f"Items: {data['items']}")
            print(f"Item locations: {data['item_locations']}")
            self.display_map(data["map"])

        elif packet_type == "map":
            self.display_map(data)
            print(f"Goblin health: {data['monster']['health']}")

        elif packet_type == "welcome":
            character = data["character"]
            scene = data["scene"]

            print(f"Class: {character['character_class']}")
            print(
                f"Starting position: "
                f"{tuple(character['position'])}"
            )
            print(f"Scene items: {scene['items']}")
            print(f"Item locations: {scene['item_locations']}")
            print(f"NPCs: {scene['npcs']}")
            self.display_map(data["map"])

        elif packet_type == "help":
            for command in data:
                print(f"- {command}")

        elif packet_type == "combat":
            character = data.get("character")
            target = data.get("target")

            if character is not None:
                print(f"Your health: {character['health']}")

            if target is not None:
                print(f"Target health: {target['health']}")

            monster = data.get("monster")

            if monster is not None:
                print(f"Goblin health: {monster['health']}")

    @staticmethod
    def display_map(map_data):
        # Most current terminals support emoji, but the fallback keeps the
        # lesson usable in older IDE consoles and Windows command windows.
        try:
            print(map_data["map"])
            print(map_data["legend"])
        except UnicodeEncodeError:
            print(map_data["ascii_map"])
            print(map_data["ascii_legend"])

    def receive_messages(self):
        # Incoming messages must be read in the background so a chat message or
        # movement update can appear while the player is choosing a command.
        reader = self.client_socket.makefile(
            "r",
            encoding="utf-8",
        )

        try:
            for line in reader:
                packet = json.loads(line)
                message = packet.get("message", "")

                if message != "":
                    print(f"\n{message}")

                self.display_data(packet)

        except (
            ConnectionResetError,
            OSError,
            json.JSONDecodeError,
        ) as error:
            if self.running:
                print(f"\nConnection error: {error}")

        finally:
            self.running = False

    def write_commands(self):
        # The client sends text commands rather than changing game state
        # directly. The server validates and applies every command.
        print("\nType help to see the commands.")

        while self.running:
            try:
                command = input("> ").strip()

                if command == "":
                    continue

                send_json(
                    self.client_socket,
                    {
                        "type": "command",
                        "command": command,
                    },
                )

                if command.lower() == "exit":
                    break

            except OSError:
                print("The command could not be sent.")
                break

        self.running = False

    def close(self):
        self.running = False

        try:
            self.client_socket.shutdown(
                socket.SHUT_RDWR
            )
        except OSError:
            pass

        try:
            self.client_socket.close()
        except OSError:
            pass

        print("Client closed.")

    def run(self):
        # One thread listens; the main thread remains available for input.
        if not self.connect():
            return

        receive_thread = threading.Thread(
            target=self.receive_messages,
            daemon=True,
        )
        receive_thread.start()

        self.write_commands()
        self.close()


if __name__ == "__main__":
    client = PlayerClient()
    client.run()
