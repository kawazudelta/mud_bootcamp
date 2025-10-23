# characters.py
# Define the blueprint for a character

class Character:
    """A simple RPG-style character"""

    # __init__ runs when you create (instantiate) a Character
    def __init__(self, name, hp, attack):
        # 'self' refers to the specific character being created.
        self.name = name      # each Character keeps its own name
        self.hp = hp          # hit points (health)
        self.attack = attack  # damage per strike

    def speak(self, message):
        """Have the character say something"""
        print(f"{self.name} says: '{message}'")

    def take_damage(self, amount):
        """Subtract damage and report remaining HP."""
        self.hp -= amount
        print(f"{self.name} takes {amount} damage! HP now {self.hp}")
        if self.hp <= 0:
            print(f"{self.name} has fallen!")
            self.drop_loot()

    def strike(self, target):
        """Attack another character."""
        print(f"{self.name} attacks {target.name} for {self.attack} damage!")
        target.take_damage(self.attack)

    def drop_loot(self):
        print(f"{self.name} drops a potion!")

class Warrior(Character):
    """A stronger subclass of Character"""
    def __init__(self, name):
        # super() calls Character.__init__
        super().__init__(name, hp=30, attack=6)

class Mage(Character):
    """A weaker magical subclass"""
    def __init__(self, name):
        super().__init__(name, hp=18, attack=4)
        self.mana = 10

    def cast_spell(self, target):
        if self.mana >= 3:
            damage = 8
            print(f"{self.name} casts Firebolt for {damage} damage!")
            target.take_damage(damage)
            self.mana -= 3
            print(f"{self.name}'s mana left: {self.mana}")
        else:
            print(f"{self.name} is out of mana!")