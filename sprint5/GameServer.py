# GameServer.py
# This file creates the connected world and controls the game.

import json
import random
import socket
import threading

from GameModels import (
    IceWizard,
    MAP_MAX,
    MAP_MIN,
    Monster,
    NPC,
    Scene,
    Warrior,
    Wizard,
)

# Emoji make the map easier to read as a game
# fallbackis text in case terminals can't display
USE_EMOJI = True

EMOJI_SYMBOLS = {
    "empty": "·",
    "you": "🧍",
    "other": "👤",
    "monster": "👹",
    "key": "🔑",
    "item": "📦",
    "exit": "🚪",
}

ASCII_SYMBOLS = {
    "empty": ".",
    "you": "P",
    "other": "O",
    "monster": "M",
    "key": "K",
    "item": "I",
    "exit": "E",
}


def send_json(connection, data):
    message = json.dumps(data) + "\n"
    connection.sendall(message.encode("utf-8"))


class PlayerSession:
    def __init__(self, connection, address, character):
        self.connection = connection
        self.address = address
        self.character = character
        self.connected = True
        self.won = False
        self.send_lock = threading.Lock()

    def send(self, message_type, message, data=None):
        # Several server threads can notify one client at the same time
        # lock prevents two JSON packets from being sent at once
        packet = {
            "type": message_type,
            "message": message,
            "data": data,
        }

        with self.send_lock:
            send_json(self.connection, packet)

    def close(self):
        self.connected = False

        try:
            self.connection.close()
        except OSError:
            pass


class GameServer:
    def __init__(self, host="0.0.0.0", port=12345):
        self.host = host
        self.port = port

        self.server_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
        )

        self.server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1,
        )

        # clients send requests, but server
        # owns positions, health, items, the Goblin, and the win condition
        self.players = {}
        self.players_lock = threading.Lock()
        self.running = True

        guide = NPC("Guide", 3, 60, "Forest Guide")
        self.exit_position = (-2, -2)
        self.monster = Monster(
            name="Goblin",
            health=45,
            position=(0, 1),
            damage=8,
        )

        self.scene = Scene(
            "Goblin's Crossing",
            7,
            npcs=[guide],
            items=[
                "Silver Key",
            ],
            item_locations={
                "Silver Key": (2, 2),
            },
        )

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Game server is listening on " f"{self.host}:{self.port}")

    def create_character(self, player_data):
        name = player_data["name"]
        character_class = player_data["character_class"]
        strength = player_data["strength"]
        intelligence = player_data["intelligence"]
        position = self.find_open_position()

        if character_class == "Warrior":
            return Warrior(
                name=name,
                skills=["strength", "parry"],
                position=position,
                strength=strength,
                intelligence=intelligence,
            )

        if character_class == "IceWizard":
            return IceWizard(
                name=name,
                skills=["magic", "intelligence", "regeneration"],
                position=position,
                strength=strength,
                intelligence=intelligence,
            )

        return Wizard(
            name=name,
            skills=["magic", "accuracy"],
            position=position,
            strength=strength,
            intelligence=intelligence,
        )

    def find_open_position(self):
        # Players cannot spawn on an objective, the Goblin, the Exit, another player
        while True:
            position = (
                random.randint(MAP_MIN, MAP_MAX),
                random.randint(MAP_MIN, MAP_MAX),
            )

            with self.players_lock:
                used_positions = {
                    session.character.position for session in self.players.values()
                }

            reserved_positions = set(self.scene.item_locations.values())
            reserved_positions.add(self.exit_position)
            reserved_positions.add(self.monster.position)

            if position not in used_positions | reserved_positions:
                return position

    def scene_data(self):
        data = self.scene.describe()
        data["exit_position"] = list(self.exit_position)
        data["monster"] = self.monster.to_dict()
        return data

    def render_map(self, viewer, use_emoji=USE_EMOJI):
        # The map is rendered from server state so every client sees the same world
        symbols = EMOJI_SYMBOLS if use_emoji else ASCII_SYMBOLS
        rows = ["     " + "  ".join(f"{x:>2}" for x in range(MAP_MIN, MAP_MAX + 1))]

        for y in range(MAP_MAX, MAP_MIN - 1, -1):
            cells = []

            for x in range(MAP_MIN, MAP_MAX + 1):
                position = (x, y)
                symbol = symbols["empty"]

                if position == self.exit_position:
                    symbol = symbols["exit"]

                for item, item_position in self.scene.item_locations.items():
                    if position == item_position:
                        symbol = (
                            symbols["key"] if item == "Silver Key" else symbols["item"]
                        )

                if self.monster.is_alive() and position == self.monster.position:
                    symbol = symbols["monster"]

                if viewer.character.position == position:
                    symbol = symbols["you"]
                else:
                    with self.players_lock:
                        other_player_here = any(
                            other_session is not viewer
                            and other_session.character.is_alive()
                            and other_session.character.position == position
                            for other_session in self.players.values()
                        )

                    if other_player_here:
                        symbol = symbols["other"]

                cells.append(symbol)

            rows.append(f"{y:>2} | " + "  ".join(cells))

        return "\n".join(rows)

    def map_data(self, viewer):
        if USE_EMOJI:
            legend = "🧍=you 👤=other player 👹=Goblin " "🔑=Silver Key 📦=item 🚪=Exit"
        else:
            legend = "P=you O=other player M=Goblin K=Silver Key I=item E=Exit"

        # The ASCII copy is sent with the emoji copy so the client can switch
        ascii_legend = "P=you O=other player M=Goblin K=Silver Key I=item E=Exit"

        return {
            "map": self.render_map(viewer, use_emoji=USE_EMOJI),
            "ascii_map": self.render_map(viewer, use_emoji=False),
            "legend": legend,
            "ascii_legend": ascii_legend,
            "monster": self.monster.to_dict(),
            "exit": list(self.exit_position),
        }

    def send_map_to_all(self):
        # Movement and combat change shared state, so every connected client
        # receives a fresh map instead of relying on a local prediction.
        with self.players_lock:
            sessions = list(self.players.values())

        for session in sessions:
            try:
                session.send(
                    "map",
                    "The shared map was updated.",
                    self.map_data(session),
                )
            except OSError:
                pass

    def broadcast(
        self,
        message_type,
        message,
        data=None,
        exclude=None,
    ):
        with self.players_lock:
            sessions = list(self.players.values())

        for session in sessions:
            if session is not exclude:
                try:
                    session.send(message_type, message, data)
                except OSError:
                    pass

    def receive_join_data(self, connection):
        reader = connection.makefile("r", encoding="utf-8")
        first_line = reader.readline()

        if first_line == "":
            return None, reader

        player_data = json.loads(first_line)

        if player_data.get("type") != "join":
            return None, reader

        return player_data, reader

    def add_player(self, connection, address):
        try:
            player_data, reader = self.receive_join_data(connection)

            if player_data is None:
                connection.close()
                return

            name = player_data.get("name", "").strip()

            if name == "":
                send_json(
                    connection,
                    {
                        "type": "error",
                        "message": "Name cannot be empty.",
                        "data": None,
                    },
                )
                connection.close()
                return

            with self.players_lock:
                name_is_used = name.lower() in {
                    player_name.lower() for player_name in self.players
                }

            if name_is_used:
                send_json(
                    connection,
                    {
                        "type": "error",
                        "message": (
                            "That name is already in use. "
                            "Reconnect with a different name."
                        ),
                        "data": None,
                    },
                )
                connection.close()
                return

            character = self.create_character(player_data)
            session = PlayerSession(connection, address, character)

            with self.players_lock:
                self.players[character.name] = session

            print(f"{character.name} connected from {address}")

            session.send(
                "welcome",
                (
                    f"Welcome to {self.scene.name}. "
                    "Find the Silver Key and survive the battle."
                ),
                {
                    "character": character.to_dict(),
                    "scene": self.scene_data(),
                    "map": self.map_data(session),
                },
            )

            self.broadcast(
                "event",
                f"{character.name} joined the game.",
                exclude=session,
            )
            self.send_map_to_all()

            player_thread = threading.Thread(
                target=self.handle_player,
                args=(session, reader),
                daemon=True,
            )
            player_thread.start()

        except (
            KeyError,
            ValueError,
            json.JSONDecodeError,
            OSError,
        ) as error:
            print(f"Could not add player: {error}")

            try:
                connection.close()
            except OSError:
                pass

    def handle_player(self, session, reader):
        try:
            for line in reader:
                if not self.running or not session.connected:
                    break

                packet = json.loads(line)

                if packet.get("type") != "command":
                    session.send(
                        "error",
                        "The server expected a command.",
                    )
                    continue

                command = packet.get("command", "")
                self.process_command(session, command)

        except (
            ConnectionResetError,
            OSError,
            json.JSONDecodeError,
        ):
            pass

        finally:
            self.remove_player(session)

    def process_command(self, session, command):
        # Commands are processed on server
        command = command.strip()
        parts = command.split()

        if len(parts) == 0:
            return

        action = parts[0].lower()
        character = session.character

        if not character.is_alive() and action not in {
            "status",
            "players",
            "scene",
            "map",
            "exit",
            "help",
        }:
            session.send("error", "You have been defeated.")
            return

        if action == "move":
            if len(parts) == 2:
                direction = parts[1].lower()
                spaces = 1
                self.move_player(session, direction, spaces)
            elif len(parts) != 3:
                    session.send(
                        "error",
                        "Use: move <direction> <spaces>",
                    )
                    return
            
            if len(parts) == 3:
                direction = parts[1].lower()
                try:
                    spaces = int(parts[2])
                except ValueError:
                    session.send("error", "Number of spaces must be an integer.")
                    return

                if spaces < 1:
                    session.send("error", "Number of spaces must be at least 1.")
                    return

                self.move_player(session, direction, spaces)


        elif action == "say":
            message = command[4:].strip()

            if message == "":
                session.send("error", "Use: say message")
                return

            self.broadcast(
                "chat",
                f"{character.name}: {message}",
            )

        elif action == "players":
            self.send_player_list(session)

        elif action == "status":
            session.send(
                "status",
                "Your current character information:",
                character.to_dict(),
            )

        elif action == "scene":
            session.send(
                "scene",
                f"You are in {self.scene.name}.",
                {
                    **self.scene_data(),
                    "map": self.map_data(session),
                },
            )

        elif action == "map":
            session.send(
                "map",
                "The shared map:",
                self.map_data(session),
            )
 
        elif action == "attack":
            if len(parts) != 2:
                session.send(
                    "error",
                    "Use: attack player_name or attack Goblin",
                )
                return

            if parts[1].lower() in {"goblin", "monster"}:
                self.attack_monster(session)
            else:
                self.attack_player(session, parts[1])

        elif action == "cast":
            if len(parts) != 3:
                session.send(
                    "error",
                    "Use: cast spell_name player_name_or_Goblin",
                )
                return

            if parts[2].lower() in {"goblin", "monster"}:
                self.cast_spell_on_monster(session, parts[1])
            else:
                self.cast_spell(session, parts[1], parts[2])

        elif action == "pick":
            if len(parts) < 3 or parts[1].lower() != "up":
                session.send("error", "Use: pick up item_name")
                return

            item_name = command.split(" ", 2)[2]
            self.pick_up_item(session, item_name)

        elif action == "talk":
            if len(parts) != 2:
                session.send("error", "Use: talk npc_name")
                return

            self.talk_to_npc(session, parts[1])

        elif action == "regenerate":
            worked, message = character.regenerate()

            if worked:
                session.send(
                    "status",
                    message,
                    character.to_dict(),
                )
            else:
                session.send("error", message)

        elif action == "help":
            self.send_help(session)

        elif action == "exit":
            session.connected = False
            session.send("event", "You left the game.")

        else:
            session.send("error", "Unknown command. Type help.")

    def move_player(self, session, direction, spaces):
        character = session.character
        original_position = character.position

        for _ in range(spaces):
            worked, message = character.move(direction)

            if not worked:
                character.position = original_position
                session.send("error", message)
                return

        with self.players_lock:
            for other_session in self.players.values():
                if other_session is session:
                    continue

                if other_session.character.position == character.position:
                    character.position = original_position
                    session.send(
                        "error",
                        f"Blocked by {other_session.character.name}.",
                    )
                    return

        session.send(
            "movement",
            message,
            character.to_dict(),
        )

        self.broadcast(
            "event",
            message,
            exclude=session,
        )
        self.send_map_to_all()

        self.check_exit(session)

    def check_exit(self, session):
        character = session.character

        if session.won:
            return

        if character.position != self.exit_position:
            return

        if "Silver Key" not in character.inventory:
            session.send(
                "objective",
                "The Exit is locked. Find the Silver Key first.",
            )
            return

        session.won = True
        session.send(
            "victory",
            "You used the Silver Key and escaped Goblin's Crossing!",
            {
                "character": character.to_dict(),
                "map": self.map_data(session),
            },
        )
        self.broadcast(
            "event",
            f"{character.name} escaped Goblin's Crossing and won the game!",
        )

    def find_player(self, target_name):
        with self.players_lock:
            for name, session in self.players.items():
                if name.lower() == target_name.lower():
                    return session

        return None

    def attack_player(self, attacker_session, target_name):
        target_session = self.find_player(target_name)

        if target_session is None:
            attacker_session.send(
                "error",
                f"{target_name} is not connected.",
            )
            return

        if target_session is attacker_session:
            attacker_session.send(
                "error",
                "You cannot attack yourself.",
            )
            return

        if not target_session.character.is_alive():
            attacker_session.send(
                "error",
                f"{target_name} has already been defeated.",
            )
            return

        result = attacker_session.character.attack(target_session.character)

        self.finish_attack(
            attacker_session,
            target_session,
            result,
        )

    def cast_spell(self, caster_session, spell_name, target_name):
        target_session = self.find_player(target_name)

        if target_session is None:
            caster_session.send(
                "error",
                f"{target_name} is not connected.",
            )
            return

        if target_session is caster_session:
            caster_session.send(
                "error",
                "You cannot cast a spell on yourself.",
            )
            return

        result = caster_session.character.cast_spell(
            spell_name,
            target_session.character,
        )

        self.finish_attack(
            caster_session,
            target_session,
            result,
        )

    def attack_monster(self, attacker_session):
        # The Goblin is shared by all players, so its health is changed only on
        # the server
        if not self.monster.is_alive():
            attacker_session.send("error", "The Goblin has already been defeated.")
            return

        result = attacker_session.character.attack(self.monster)

        if not result["success"]:
            attacker_session.send("error", result["message"])
            return

        attacker_session.send(
            "combat",
            result["message"],
            {
                "character": attacker_session.character.to_dict(),
                "monster": self.monster.to_dict(),
            },
        )
        self.broadcast("event", result["message"], exclude=attacker_session)

        if self.monster.is_alive():
            self.monster_counterattack(attacker_session)
        else:
            self.broadcast(
                "event",
                "The Goblin has been defeated. The Silver Key can now be claimed.",
            )

        self.send_map_to_all()

    def cast_spell_on_monster(self, caster_session, spell_name):
        if not self.monster.is_alive():
            caster_session.send("error", "The Goblin has already been defeated.")
            return

        result = caster_session.character.cast_spell(
            spell_name,
            self.monster,
        )

        if not result["success"]:
            caster_session.send("error", result["message"])
            return

        caster_session.send(
            "combat",
            result["message"],
            {
                "character": caster_session.character.to_dict(),
                "monster": self.monster.to_dict(),
            },
        )
        self.broadcast("event", result["message"], exclude=caster_session)

        if self.monster.is_alive():
            self.monster_counterattack(caster_session)
        else:
            self.broadcast(
                "event",
                "The Goblin has been defeated. The Silver Key can now be claimed.",
            )

        self.send_map_to_all()

    def monster_counterattack(self, player_session):
        # The Goblin retaliates only at melee distance

        if self.monster.distance_to(player_session.character) > 1:
            return

        result = self.monster.attack(player_session.character)

        if not result["success"]:
            return

        player_session.send(
            "combat",
            result["message"],
            {
                "character": player_session.character.to_dict(),
                "monster": self.monster.to_dict(),
            },
        )
        self.broadcast("event", result["message"], exclude=player_session)

        if not player_session.character.is_alive():
            self.broadcast(
                "event",
                f"{player_session.character.name} was defeated by the Goblin.",
            )

    def finish_attack(self, attacker_session, target_session, result):
        if not result["success"]:
            attacker_session.send("error", result["message"])
            return

        attacker_session.send(
            "combat",
            result["message"],
            {"target": target_session.character.to_dict()},
        )

        target_session.send(
            "combat",
            result["message"],
            {"character": target_session.character.to_dict()},
        )

        self.broadcast("event", result["message"])

        if not target_session.character.is_alive():
            self.broadcast(
                "event",
                f"{target_session.character.name} has been defeated.",
            )

        self.send_map_to_all()

    def send_player_list(self, requester):
        with self.players_lock:
            player_data = [
                session.character.to_dict() for session in self.players.values()
            ]

        requester.send(
            "players",
            "Players currently in the game:",
            player_data,
        )

    def pick_up_item(self, session, requested_item):
        matching_item = None

        for item in self.scene.items:
            if item.lower() == requested_item.lower():
                matching_item = item
                break

        if matching_item is None:
            session.send(
                "error",
                f"{requested_item} is not in the scene.",
            )
            return

        # key is the reward for defeating the Goblin
        if matching_item == "Silver Key" and self.monster.is_alive():
            session.send(
                "error",
                "The Goblin is guarding the Silver Key. Defeat it first.",
            )
            return

        item_position = self.scene.item_locations[matching_item]

        if session.character.position != item_position:
            session.send(
                "error",
                (
                    f"{matching_item} is at {item_position}. "
                    f"Move there before picking it up."
                ),
            )
            return

        worked, message = session.character.pick_up(matching_item)

        if not worked:
            session.send("error", message)
            return

        self.scene.remove_item(matching_item)

        session.send(
            "inventory",
            message,
            session.character.to_dict(),
        )

        self.broadcast(
            "event",
            message,
            exclude=session,
        )
        self.send_map_to_all()
        self.check_exit(session)

    def talk_to_npc(self, session, npc_name):
        for npc in self.scene.npcs:
            if npc.name.lower() == npc_name.lower():
                session.send("npc", npc.talk())
                return

        session.send(
            "error",
            f"{npc_name} is not in this scene.",
        )

    def send_help(self, session):
        commands = [
            "move up",
            "move down",
            "move left",
            "move right",
            "map",
            "say message",
            "players",
            "status",
            "scene",
            "attack Goblin",
            "attack player_name",
            "cast fireball Goblin",
            "cast lightningstrike Goblin",
            "cast windstorm Goblin",
            "cast spell_name player_name",
            "gravity player_name",
            "instakill player_name"
            "pick up Silver Key",
            "talk Guide",
            "regenerate",
            "help",
            "exit",
        ]

        session.send(
            "help",
            "Goal: defeat the Goblin, collect the Silver Key, then reach E.\n"
            "Available commands:",
            commands,
        )

    def remove_player(self, session):
        character_name = session.character.name
        removed = False

        with self.players_lock:
            current_session = self.players.get(character_name)

            if current_session is session:
                del self.players[character_name]
                removed = True

        session.close()

        if removed:
            print(f"{character_name} disconnected.")
            self.broadcast(
                "event",
                f"{character_name} left the game.",
            )

    def shutdown(self):
        self.running = False

        try:
            self.server_socket.close()
        except OSError:
            pass

        with self.players_lock:
            sessions = list(self.players.values())

        for session in sessions:
            try:
                session.send(
                    "event",
                    "The server is shutting down.",
                )
            except OSError:
                pass

            session.close()

        print("Server closed.")

    def run(self):
        try:
            self.start()

            while self.running:
                try:
                    connection, address = self.server_socket.accept()
                    self.add_player(connection, address)
                except OSError:
                    break

        except KeyboardInterrupt:
            print("\nServer stopped by the user.")

        finally:
            self.shutdown()


if __name__ == "__main__":
    game_server = GameServer()
    game_server.run()
