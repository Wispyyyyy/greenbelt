# GameModels.py
# This file keeps the game classes from the earlier OOP project.

VERIFIED_SKILLS = [
    "dodge",
    "speed",
    "strength",
    "parry",
    "intelligence",
    "magic",
    "regeneration",
    "accuracy",
    "dexterity",
    "cunning",
    "precision",
    "luck",
    "stealth",
]


# Keeping spell data in one table makes it easy to add a spell without
# rewriting the combat method. The server still decides when a spell is used.
SPELLS = {
    "fireball": {"damage": 20, "range": 5},
    "lightningstrike": {"damage": 25, "range": 8},
    "windstorm": {"damage": 15, "range": 4},
    "gravity": {"damage": 57, "range": 8},
    "ultimatemove": {"damage": -10, "range": 8},
}


# small coordinate system keeps the ASCII maprocess_command()p readable in a terminal
MAP_MIN = -3
MAP_MAX = 3


class VideoGameCharacter:
    def __init__(
        self,
        name="Player",
        level=1,
        health=100,
        skills=None,
        item_capacity=10,
        position=(0, 0),
        inventory=None,
        strength=5,
        intelligence=5,
    ):
        if skills is None:
            skills = ["speed", "strength"]

        if inventory is None:
            inventory = {}

        self._name = "Player"
        self.__level = 1
        self.__health = 100
        self._skills = []
        self._item_capacity = 10
        self._position = (0, 0)
        self._inventory = {}
        self._strength = 5
        self._intelligence = 5

        self.name = name
        self.level = level
        self.health = health
        self.skills = skills
        self.item_capacity = item_capacity
        self.position = position
        self.inventory = inventory
        self.strength = strength
        self.intelligence = intelligence

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, new_name):
        if type(new_name) != str:
            raise ValueError("Name must be a string.")

        new_name = new_name.strip()

        if len(new_name) < 1 or len(new_name) > 20:
            raise ValueError("Name must be between 1 and 20 characters.")

        self._name = new_name

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, new_level):
        if type(new_level) != int:
            raise ValueError("The level must be an integer.")

        if new_level < 1:
            raise ValueError("The level must be greater than zero.")

        self.__level = new_level

    @property
    def health(self):
        return self.__health

    @health.setter
    def health(self, new_health):
        if type(new_health) != int:
            raise ValueError("Health must be an integer.")

        if new_health < 0 or new_health > 100:
            raise ValueError("Health must be between 0 and 100.")

        self.__health = new_health

    @property
    def skills(self):
        return self._skills.copy()

    @skills.setter
    def skills(self, new_skills):
        if type(new_skills) != list:
            raise ValueError("Skills must be a list.")

        if len(new_skills) > 5:
            raise ValueError("Max skills cap reached.")

        for skill in new_skills:
            if skill not in VERIFIED_SKILLS:
                raise ValueError(f"{skill} is not a valid skill.")

        self._skills = new_skills.copy()

    @property
    def item_capacity(self):
        return self._item_capacity

    @item_capacity.setter
    def item_capacity(self, new_item_capacity):
        if type(new_item_capacity) != int:
            raise ValueError("Item capacity must be an integer.")

        if new_item_capacity < 1 or new_item_capacity > 20:
            raise ValueError("Item capacity must be between 1 and 20.")

        self._item_capacity = new_item_capacity

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, new_position):
        if type(new_position) != tuple and type(new_position) != list:
            raise ValueError("Position must be a tuple or list.")

        if len(new_position) != 2:
            raise ValueError("Position must have two coordinates.")

        x = new_position[0]
        y = new_position[1]

        if type(x) != int or type(y) != int:
            raise ValueError("Both coordinates must be integers.")

        self._position = (x, y)

    @property
    def inventory(self):
        return self._inventory.copy()

    @inventory.setter
    def inventory(self, new_inventory):
        if type(new_inventory) != dict:
            raise ValueError("Inventory must be a dictionary.")

        self._inventory = new_inventory.copy()

    @property
    def strength(self):
        return self._strength

    @strength.setter
    def strength(self, new_strength):
        if type(new_strength) != int:
            raise ValueError("Strength must be an integer.")

        if new_strength < 1 or new_strength > 10:
            raise ValueError("Strength must be between 1 and 10.")

        self._strength = new_strength

    @property
    def intelligence(self):
        return self._intelligence

    @intelligence.setter
    def intelligence(self, new_intelligence):
        if type(new_intelligence) != int:
            raise ValueError("Intelligence must be an integer.")

        if new_intelligence < 1 or new_intelligence > 10:
            raise ValueError("Intelligence must be between 1 and 10.")

        self._intelligence = new_intelligence

    def move(self, direction):
        # Characters calculate their own movement, but the server remains
        # responsible for checking collisions with other connected players.
        x, y = self.position

        if direction == "up":
            y += 1
        elif direction == "down":
            y -= 1
        elif direction == "right":
            x += 1
        elif direction == "left":
            x -= 1
        else:
            return False, "Use up, down, left, or right."

        if x < MAP_MIN or x > MAP_MAX or y < MAP_MIN or y > MAP_MAX:
            return False, (
                f"You cannot move outside the " f"{MAP_MIN} to {MAP_MAX} game area."
            )

        self.position = (x, y)

        return True, (
            f"{self.name} moved {direction}. " f"Current position: {self.position}"
        )

    def interact(self, game_object):
        return f"{self.name} interacts with {game_object}."

    def pick_up(self, item):
        if len(self._inventory) >= self.item_capacity:
            return False, "Inventory is full."

        self._inventory[item] = "Item"
        return True, f"{self.name} picked up {item}."

    def attack(self, target):
        # Combat returns structured data instead of printing so the server can
        # send the same result to the attacker, target, and other players.
        if not target.is_alive():
            return {
                "success": False,
                "message": f"{target.name} has already been defeated.",
            }

        if self.distance_to(target) > 1:
            return {
                "success": False,
                "message": f"{target.name} is too far away.",
            }

        damage = 5 + self.strength
        target.take_damage(damage)

        return {
            "success": True,
            "damage": damage,
            "message": (f"{self.name} attacked {target.name} " f"for {damage} damage."),
        }

    def cast_spell(self, spell_name, target):
        # Range and skill checks belong to the character model because they
        # describe game rules, not socket behavior.
        spell_name = spell_name.lower()

        if spell_name not in SPELLS:
            return {
                "success": False,
                "message": f"{spell_name} is not a valid spell.",
            }

        if "magic" not in self.skills:
            return {
                "success": False,
                "message": f"{self.name} does not have the magic skill.",
            }

        if not target.is_alive():
            return {
                "success": False,
                "message": f"{target.name} has already been defeated.",
            }

        spell = SPELLS[spell_name]
        distance = self.distance_to(target)

        if distance > spell["range"]:
            return {
                "success": False,
                "message": (
                    f"{target.name} is too far away. "
                    f"{spell_name} has a range of {spell['range']}."
                ),
            }

        damage = spell["damage"] + self.intelligence
        target.take_damage(damage)

        return {
            "success": True,
            "spell": spell_name,
            "damage": damage,
            "target_health": target.health,
            "message": (
                f"{self.name} cast {spell_name} on "
                f"{target.name} for {damage} damage."
            ),
        }

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        return self.health

    def regenerate(self, amount=5):
        if "regeneration" not in self.skills:
            return False, f"{self.name} does not have regeneration."

        old_health = self.health
        self.health = min(100, self.health + amount)
        healed = self.health - old_health

        return True, f"{self.name} regenerated {healed} health."

    def distance_to(self, other_character):
        x1, y1 = self.position
        x2, y2 = other_character.position
        return abs(x1 - x2) + abs(y1 - y2)

    def to_dict(self):
        # JSON cannot serialize custom Python objects, so network messages use
        # plain dictionaries and lists as their shared representation.
        return {
            "name": self.name,
            "character_class": self.__class__.__name__,
            "level": self.level,
            "health": self.health,
            "skills": self.skills,
            "item_capacity": self.item_capacity,
            "position": list(self.position),
            "inventory": self.inventory,
            "strength": self.strength,
            "intelligence": self.intelligence,
        }


class Warrior(VideoGameCharacter):
    # These overrides demonstrate polymorphism: the server can call move or
    # attack on any character without knowing which class was selected.
    def move(self, direction):
        worked, message = super().move(direction)

        if worked:
            message = message.replace("moved", "charged")

        return worked, message

    def attack(self, target):
        if not target.is_alive():
            return {
                "success": False,
                "message": f"{target.name} has already been defeated.",
            }

        if self.distance_to(target) > 1:
            return {
                "success": False,
                "message": f"{target.name} is too far away.",
            }

        damage = 10 + self.strength
        target.take_damage(damage)

        return {
            "success": True,
            "damage": damage,
            "message": (
                f"{self.name} swung a sword at {target.name} " f"for {damage} damage."
            ),
        }


class Wizard(VideoGameCharacter):
    def move(self, direction):
        worked, message = super().move(direction)

        if worked:
            message = message.replace("moved", "teleported")

        return worked, message

    def attack(self, target):
        return self.cast_spell("fireball", target)


class IceWizard(Wizard):
    def attack(self, target):
        if not target.is_alive():
            return {
                "success": False,
                "message": f"{target.name} has already been defeated.",
            }

        if self.distance_to(target) > 5:
            return {
                "success": False,
                "message": f"{target.name} is too far away.",
            }

        damage = 15 + self.intelligence
        target.take_damage(damage)

        return {
            "success": True,
            "damage": damage,
            "message": (f"{self.name} froze {target.name} " f"for {damage} damage."),
        }


class Monster:
    # The Goblin follows the same small combat interface as a character. That
    # allows a player to attack either another player or the Goblin object.
    def __init__(self, name="Goblin", health=45, position=(0, 1), damage=8):
        self.name = name
        self.health = health
        self.position = position
        self.damage = damage

    def is_alive(self):
        return self.health > 0

    def take_damage(self, damage):
        self.health = max(0, self.health - damage)
        return self.health

    def distance_to(self, other_character):
        x1, y1 = self.position
        x2, y2 = other_character.position
        return abs(x1 - x2) + abs(y1 - y2)

    def attack(self, target):
        if not self.is_alive() or not target.is_alive():
            return {
                "success": False,
                "message": f"{self.name} cannot attack right now.",
            }

        if self.distance_to(target) > 1:
            return {
                "success": False,
                "message": f"{self.name} is too far away to attack.",
            }

        target.take_damage(self.damage)
        return {
            "success": True,
            "damage": self.damage,
            "message": (
                f"{self.name} attacked {target.name} " f"for {self.damage} damage."
            ),
        }

    def to_dict(self):
        return {
            "name": self.name,
            "health": self.health,
            "position": list(self.position),
            "damage": self.damage,
            "alive": self.is_alive(),
        }


class NPC(VideoGameCharacter):
    def __init__(self, name, level=1, health=100, role="NPC"):
        super().__init__(name=name, level=level, health=health)
        self.role = role

    def perform_action(self):
        return f"{self.name} the {self.role} is doing something."

    def talk(self):
        return (
            f"{self.name}: Defeat the Goblin, claim the Silver Key, "
            "then reach the Exit."
        )


class Scene:
    def __init__(self, name, size, npcs=None, items=None, item_locations=None):
        if npcs is None:
            npcs = []

        if items is None:
            items = []

        if item_locations is None:
            item_locations = {}

        self.name = name
        self.size = size
        self.npcs = npcs
        self.items = items
        # Item names alone are not enough for a map game; each item needs a
        # coordinate so the server can prevent pickup from anywhere.
        self.item_locations = item_locations.copy()

    def describe(self):
        return {
            "name": self.name,
            "size": self.size,
            "npcs": [npc.name for npc in self.npcs],
            "items": self.items.copy(),
            "item_locations": {
                item: list(self.item_locations[item]) for item in self.items
            },
        }

    def add_npc(self, npc):
        self.npcs.append(npc)

    def remove_npc(self, npc):
        if npc in self.npcs:
            self.npcs.remove(npc)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            self.item_locations.pop(item, None)
