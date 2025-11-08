# MUD Class System Architecture

This document outlines a proposed high-level module and class structure for a flexible, multi-class system in Evennia. This approach prioritizes separation of concerns, making the code easier to manage, extend, and debug.

## The Core Concept: Data vs. Logic

The key is to separate the *definitions* of your classes (what a Warrior is, what skills it gets) from the *character's personal progress* in that class (the fact that *your character* is a Level 5 Warrior with 1250 XP).

We will create three main components:

1.  **Class Definitions (`world/classes.py`):** A central "database" of all available classes and their properties. This is pure data.
2.  **The Class Handler (`world/class_handler.py`):** A dedicated logic controller that manages gaining XP, leveling up, and swapping classes for a *single character*.
3.  **The Character (`typeclasses/characters.py`):** Your character will store its personal class data and use the Class Handler to manage it.

---

## 1. The Class Definitions (`world/classes.py`)

Create a new file to store the "templates" for every class in your game. Using a Python dictionary is a great way to start. This file doesn't contain any game logic, just the static rules.

```python
# world/classes.py

# This dictionary holds the template for every class.
# By putting it here, we can easily add new classes without
# touching any other part of the game's code.

CLASSES = {
    "warrior": {
        "name": "Warrior",
        "desc": "A master of arms and armor, strong and resilient.",
        # XP needed to reach the next level (index 0 is level 1)
        "xp_table": [0, 100, 300, 650, 1200],
        # Skills/abilities granted at each level
        "abilities": {
            1: "slash",
            3: "shield_block",
            5: "power_strike"
        }
    },
    "mage": {
        "name": "Mage",
        "desc": "A wielder of arcane energies, intelligent but fragile.",
        "xp_table": [0, 120, 350, 700, 1300],
        "abilities": {
            1: "firebolt",
            2: "light",
            5: "frost_armor"
        }
    },
    # ... add more classes like "rogue", "cleric", etc. here
}
```

## 2. The Class Handler (`world/class_handler.py`)

This is the brain of the system. It's a Python class that you will attach to your character. It contains all the methods for managing class-related actions.

```python
# world/class_handler.py

from world.classes import CLASSES

class ClassHandler:
    """
    This handler is responsible for all class and leveling logic.
    An instance of this will be attached to the character.
    """
    def __init__(self, character):
        """
        Initializes the handler, linking it to a character.
        """
        self.char = character
        # Ensure the character has the necessary storage attributes
        if not self.char.db.classes:
            self.char.db.classes = {}  # e.g., {"warrior": {"level": 1, "xp": 0}}
        if not self.char.db.active_class:
            self.char.db.active_class = None

    def add(self, class_name):
        """Adds a new class to the character, starting at level 1."""
        if class_name not in CLASSES or class_name in self.char.db.classes:
            return False
        self.char.db.classes[class_name] = {"level": 1, "xp": 0}
        if not self.char.db.active_class:
            self.swap_to(class_name)
        return True

    def swap_to(self, class_name):
        """Swaps the character's active class."""
        if class_name not in self.char.db.classes:
            return False
        self.char.db.active_class = class_name
        self.char.msg(f"You are now a {CLASSES[class_name]['name']}.")
        return True

    def gain_xp(self, amount):
        """Gains XP in the currently active class and checks for level up."""
        if not self.char.db.active_class:
            return

        active = self.char.db.active_class
        progress = self.char.db.classes[active]
        progress["xp"] += amount
        self.char.msg(f"You gain {amount} XP.")
        
        # Check for level up
        self.check_for_levelup()

    def check_for_levelup(self):
        """Checks if the character has enough XP to level up."""
        active = self.char.db.active_class
        progress = self.char.db.classes[active]
        class_template = CLASSES[active]
        
        current_level = progress["level"]
        xp_needed = class_template["xp_table"][current_level]

        if progress["xp"] >= xp_needed:
            self.level_up()

    def level_up(self):
        """Handles the actual process of leveling up."""
        # ... (increment level, grant new abilities, etc.)
        self.char.msg("You leveled up!")

```

## 3. The Character Integration (`typeclasses/characters.py`)

Finally, you'll modify your `Character` typeclass to use this new system.

```python
# typeclasses/characters.py

# ... (other imports)
from world.class_handler import ClassHandler

class Character(ObjectParent, DefaultCharacter):
    # ... (your other character methods)

    def at_object_creation(self):
        """Called only when the character is first created."""
        super().at_object_creation()
        # Initialize the storage for class data
        self.db.classes = {}
        self.db.active_class = None
        # Attach the handler
        self.class_handler = ClassHandler(self)
        # Maybe give a starting class
        self.class_handler.add("warrior")

    def at_init(self):
        """
        This is called every time the character is loaded from the database.
        We need to re-attach the handler here because the handler itself
        is not stored in the database.
        """
        self.class_handler = ClassHandler(self)

```

### Why This Approach is Best

*   **Scalability:** To add a new class, you only have to edit the `CLASSES` dictionary in `world/classes.py`. You don't need to change any logic in the character or handler.
*   **Maintainability:** All your leveling logic is in one place (`class_handler.py`). If there's a bug with gaining XP, you know exactly where to look.
*   **Clarity:** The `Character` class isn't cluttered with dozens of methods for leveling. It just holds the data and delegates the work to the handler.
*   **Flexibility:** This structure makes it easy to add more features later, like prestige classes, by simply adding new data to the class definitions and new methods to the handler.

---

## Detailed Breakdown of `classes.py`

The structure of `classes.py` is a common and powerful pattern in programming. It is not a class or a function; it's a **data structure**. Specifically, it's a **nested dictionary**. Think of it like a filing cabinet for your game's class information.

### 1. The Main Dictionary: The Filing Cabinet

The entire `CLASSES = { ... }` block defines one big Python **dictionary**.

*   **Purpose:** To hold all the different character classes.
*   **Keys:** The main keys are the simple, lowercase names of the classes: `"warrior"`, `"mage"`, etc. These are the internal IDs you'll use in your code.
*   **Values:** The value for each key is *another dictionary* that contains all the specific details for that class.

```python
CLASSES = {
    "warrior": { ... warrior details ... },  # The "warrior" file drawer
    "mage":    { ... mage details ... },     # The "mage" file drawer
    # "rogue":   { ... rogue details ... }      # etc.
}
```

### 2. The Inner Dictionaries: The File Folders

Now let's look inside one of the "drawers," like the one for `"warrior"`. This is where the nested part comes in.

```python
"warrior": {
    "name": "Warrior",
    "desc": "A master of arms and armor, strong and resilient.",
    "xp_table": [0, 100, 300, 650, 1200],
    "abilities": {
        1: "slash",
        3: "shield_block",
        5: "power_strike"
    }
}
```

This inner dictionary is a collection of key-value pairs that define what a Warrior is.

*   **`"name": "Warrior"`**
    *   A simple string. This is the pretty, capitalized name you show to players. We keep it separate from the lowercase key (`"warrior"`) so you can change the display name without breaking your code.

*   **`"desc": "..."`**
    *   A string for the class description, used in a `help` file or `class` command.

*   **`"xp_table": [0, 100, 300, 650, 1200]`**
    *   This is a **list** (or array) of numbers. It defines the total XP required to reach the next level. The position in the list (its "index") corresponds to a character's *current* level.
    *   `xp_table[0]` (value `0`): You are level 1 at 0 XP.
    *   `xp_table[1]` (value `100`): To get from level 1 to level 2, you need 100 total XP.
    *   `xp_table[2]` (value `300`): To get from level 2 to level 3, you need 300 total XP.
    *   In the `ClassHandler`, you would check if `character.db.classes['warrior']['xp'] >= xp_table[current_level]`.

*   **`"abilities": { ... }`**
    *   This is another **dictionary**. It maps the *level* a character attains to the *ability* they learn at that level.
    *   `1: "slash"`: At level 1, you learn the "slash" ability.
    *   `3: "shield_block"`: At level 3, you learn "shield_block".
    *   When a character levels up, your `level_up` function would look in this dictionary to see if the new level is a key. If it is, you grant them the corresponding ability.

### Why Use This Format?

1.  **Centralized:** All the rules for every class are in one human-readable file.
2.  **Easy to Add/Edit:** To create a new "Rogue" class, you just copy the "warrior" block, change the key to `"rogue"`, and edit the values. You don't have to touch any other files.
3.  **Separates Data from Logic:** This file is pure **data**. The `ClassHandler` is pure **logic**. The handler reads the data from this file to make decisions. This separation makes your code incredibly clean and easy to manage.

---

## Handling Universal Skills

The need for both class-specific and universal abilities is a common feature in RPGs, and the structure we've laid out can be easily extended to support it.

The best way to handle this is to treat universal skills as a **separate, parallel system** that lives alongside the class system. This keeps the logic clean and avoids complicating the class handler with things that aren't strictly related to classes.

Here’s how we would modify the structure:

### 1. Create a Central Skill "Database" (`world/skills.py`)

Instead of defining abilities as simple strings inside the `CLASSES` dictionary, it's better to create a central file that defines *all* abilities in the game. This makes them easier to manage.

Create a new file: `world/skills.py`

```python
# world/skills.py

SKILLS = {
    # --- Warrior Abilities ---
    "slash": {
        "name": "Slash",
        "desc": "A basic melee attack.",
        "type": "class",
        "class": "warrior"
    },
    "shield_block": {
        "name": "Shield Block",
        "desc": "Attempt to block an incoming attack.",
        "type": "class",
        "class": "warrior"
    },

    # --- Universal Skills ---
    "sprint": {
        "name": "Sprint",
        "desc": "Briefly increase your movement speed.",
        "type": "universal"
    },
    "first_aid": {
        "name": "First Aid",
        "desc": "Perform basic wound care to restore a small amount of health.",
        "type": "universal"
    }
}
```
**What we did:**
*   We created a single dictionary for all skills.
*   Each skill now has a `type` key, which can be `"class"` or `"universal"`.
*   Class skills also have a `class` key to know who they belong to.

### 2. Store Universal Skills on the Character

Now, we'll add a new attribute to the character to store the universal skills they have learned. This will be a simple list.

In `typeclasses/characters.py`:

```python
# typeclasses/characters.py

# ... (imports)

class Character(ObjectParent, DefaultCharacter):
    # ...

    def at_object_creation(self):
        """Called only when the character is first created."""
        super().at_object_creation()
        # --- Class System ---
        self.db.classes = {}
        self.db.active_class = None
        self.class_handler = ClassHandler(self)
        self.class_handler.add("warrior")

        # --- NEW: Universal Skills Storage ---
        self.db.universal_skills = []

    def at_init(self):
        """Called every time the character is loaded."""
        self.class_handler = ClassHandler(self)

    # --- NEW: Method to learn a universal skill ---
    def learn_universal_skill(self, skill_key):
        """
        Adds a universal skill to this character.
        This could be called by a trainer, a quest, or from using an item.
        """
        if skill_key not in self.db.universal_skills:
            self.db.universal_skills.append(skill_key)
            self.msg(f"You have learned a new skill: {SKILLS[skill_key]['name']}.")
            return True
        return False
```
**What we did:**
*   We added `self.db.universal_skills = []` to store the keys of the universal skills the character knows.
*   We added a helper method, `learn_universal_skill`, which you can call from anywhere (quests, trainers, etc.) to grant a new universal skill.

### 3. Update the Command Logic to Check Both

Finally, when a player tries to use an ability, the command's logic needs to check if they have access to it, either through their active class or their list of universal skills.

Here is a conceptual example of a generic `use` command:

```python
# In a command file

from commands.command import Command
from world.skills import SKILLS
from world.classes import CLASSES

class CmdUse(Command):
    key = "use"
    # ...

    def func(self):
        caller = self.caller
        skill_to_use = self.args.strip() # e.g., "slash" or "sprint"

        if skill_to_use not in SKILLS:
            caller.msg("That is not a valid skill.")
            return

        # --- The New, Combined Check ---
        has_skill = False

        # 1. Is it a universal skill they have learned?
        if skill_to_use in caller.db.universal_skills:
            has_skill = True

        # 2. If not, is it an ability from their active class?
        if not has_skill and caller.db.active_class:
            active_class = caller.db.active_class
            class_progress = caller.db.classes[active_class]
            class_abilities = CLASSES[active_class]["abilities"]

            # Check if the class can learn this skill at or below the character's level
            for level, ability_key in class_abilities.items():
                if ability_key == skill_to_use and class_progress["level"] >= level:
                    has_skill = True
                    break
        
        # --- Final Decision ---
        if has_skill:
            caller.msg(f"You use {SKILLS[skill_to_use]['name']}!")
            # ... (execute skill logic)
        else:
            caller.msg("You don't know how to do that.")

```

### Summary of this Approach

*   **Clean Separation:** Class abilities are managed by the `ClassHandler`. Universal skills are managed directly on the `Character`. The two systems don't interfere with each other.
*   **Centralized Definitions:** All skills, regardless of type, are defined in one place (`world/skills.py`), making them easy to find and edit.
*   **Flexible Logic:** The command that handles ability usage simply checks both possible sources for the skill, making the system flexible and easy to expand.

---

## Extending the System with Subclasses (FFXI-Style)

This section details how to evolve the class architecture to support a main class and a subclass, where the subclass's effective level is capped at half the main class's level.

### 1. Update Character Data Storage (`typeclasses/characters.py`)

First, we need to track the main class and subclass separately. The term `active_class` is no longer specific enough.

```python
# typeclasses/characters.py

# ... (imports)
from world.class_handler import ClassHandler
from world.skills import SKILLS # Assuming skills.py exists

class Character(ObjectParent, DefaultCharacter):
    # ...

    def at_object_creation(self):
        """Called only when the character is first created."""
        super().at_object_creation()
        # --- Class System ---
        self.db.classes = {}
        # RENAME self.db.active_class to self.db.main_class
        self.db.main_class = None
        # ADD self.db.sub_class
        self.db.sub_class = None
        
        # --- Universal Skills Storage ---
        self.db.universal_skills = []

        # Attach the handler
        self.class_handler = ClassHandler(self)
        # Maybe give a starting class
        self.class_handler.add("warrior")
        self.class_handler.set_job("warrior") # Set the initial job

    def at_init(self):
        """Called every time the character is loaded."""
        self.class_handler = ClassHandler(self)

    def learn_universal_skill(self, skill_key):
        # ... (this method remains the same)
```

**What we changed:**
*   Renamed `db.active_class` to `db.main_class` for clarity.
*   Added `db.sub_class` to store the key of the chosen subclass.

### 2. Overhaul the Class Handler (`world/class_handler.py`)

This is where the most significant changes will happen. The handler will now manage the main/sub job combination and calculate the character's effective abilities.

```python
# world/class_handler.py

from world.classes import CLASSES

class ClassHandler:
    """
    This handler is responsible for all class and leveling logic,
    including main and subclass combinations.
    """
    def __init__(self, character):
        self.char = character
        # Update to look for the new attributes
        if not self.char.db.classes:
            self.char.db.classes = {}
        if not self.char.db.main_class:
            self.char.db.main_class = None
        if not self.char.db.sub_class:
            self.char.db.sub_class = None

    def add(self, class_name):
        # ... (this method remains the same)

    def set_job(self, main_key, sub_key=None):
        """
        Sets the character's main and sub jobs.
        """
        # Validation checks
        if main_key not in self.char.db.classes:
            self.char.msg(f"You have not unlocked the {main_key} class.")
            return False
        if sub_key and sub_key not in self.char.db.classes:
            self.char.msg(f"You have not unlocked the {sub_key} class.")
            return False
        if main_key == sub_key:
            self.char.msg("Your main class and subclass cannot be the same.")
            return False

        self.char.db.main_class = main_key
        self.char.db.sub_class = sub_key

        # Provide feedback to the player
        main_name = CLASSES[main_key]['name']
        if sub_key:
            sub_name = CLASSES[sub_key]['name']
            self.char.msg(f"You are now a {main_name} / {sub_name}.")
        else:
            self.char.msg(f"You are now a {main_name}.")
        return True

    def gain_xp(self, amount):
        """Gains XP in the currently active MAIN class."""
        # This now correctly targets the main class
        if not self.char.db.main_class:
            return

        main_class = self.char.db.main_class
        progress = self.char.db.classes[main_class]
        progress["xp"] += amount
        self.char.msg(f"You gain {amount} XP.")
        self.check_for_levelup()

    def check_for_levelup(self):
        # This also correctly targets the main class
        # ... (logic is the same, but uses self.char.db.main_class)

    def level_up(self):
        # ... (logic is the same)

    def get_active_abilities(self):
        """
        Calculates and returns a list of all abilities the character
        can currently use from their main class, subclass, and universal skills.
        This is the new core of the system.
        """
        # Using a set to prevent duplicates, then converting to a list
        abilities = set()

        # 1. Add Universal Skills
        for skill in self.char.db.universal_skills:
            abilities.add(skill)

        # 2. Add Main Class Abilities
        main_key = self.char.db.main_class
        if not main_key:
            return list(abilities) # Return just universal skills if no main class
        
        main_progress = self.char.db.classes[main_key]
        main_level = main_progress["level"]
        main_class_abilities = CLASSES[main_key]["abilities"]

        for level_req, ability_key in main_class_abilities.items():
            if main_level >= level_req:
                abilities.add(ability_key)

        # 3. Add Subclass Abilities (with level cap)
        sub_key = self.char.db.sub_class
        if not sub_key:
            return list(abilities) # Return universal + main if no sub class

        sub_progress = self.char.db.classes[sub_key]
        # The FFXI Rule: Subclass level is capped at half of main class level
        effective_sub_level = main_level // 2
        
        sub_class_abilities = CLASSES[sub_key]["abilities"]
        for level_req, ability_key in sub_class_abilities.items():
            if effective_sub_level >= level_req:
                abilities.add(ability_key)

        return list(abilities)
```

**What we changed:**
*   The handler now tracks `main_class` and `sub_class`.
*   `swap_to` is replaced with a more robust `set_job` command that handles both slots.
*   `gain_xp` and `check_for_levelup` are now correctly tied to the `main_class` only.
*   The new `get_active_abilities` method is the most important addition. It consolidates all the rules: it gets universal skills, full-level main class abilities, and half-level subclass abilities, returning a single, clean list of what the player can do *right now*.

---

### 3. Simplify the Command Logic (`CmdUse`)

Because the `ClassHandler` is now so much smarter, the command for using an ability becomes incredibly simple. It doesn't need to know any of the rules; it just has to ask the handler for the final list.

```python
# In a command file

from commands.command import Command
from world.skills import SKILLS

class CmdUse(Command):
    key = "use"
    # ...

    def func(self):
        caller = self.caller
        skill_to_use = self.args.strip()

        if skill_to_use not in SKILLS:
            caller.msg("That is not a valid skill.")
            return

        # The new, simplified check
        allowed_abilities = caller.class_handler.get_active_abilities()

        if skill_to_use in allowed_abilities:
            caller.msg(f"You use {SKILLS[skill_to_use]['name']}!")
            # ... (execute skill logic)
        else:
            caller.msg("You can't do that right now.")
```

### Why This Design Works

*   **Centralized Logic:** All the complex rules for calculating effective levels and abilities are in one place: `ClassHandler.get_active_abilities`. If you want to change the level cap or add new rules, you only edit that one method.
*   **Simple Commands:** Your commands don't need to know *why* a character can use a skill, only *if* they can. This makes them very easy to write and maintain.
*   **Preserves Data Separation:** The `classes.py` and `skills.py` files remain pure data, untouched by this logic change. The system is still just as scalable as before.
