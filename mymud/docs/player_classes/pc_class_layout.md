# Player Class System Implementation Layout

This document details the architectural breakdown for implementing the PC Class System in TessMUD, incorporating the Primary/Secondary job mechanics.

## 1. Core Principles

*   **Logic/Data Separation:** Class rules (data) are strictly separated from character state (logic).
*   **Evennia Native:** Utilizing `traits` for numerical progression (XP, Level) to avoid re-inventing the wheel.
*   **Handler Pattern:** A dedicated `ClassHandler` abstracts all complexity from the Character typeclass.

## 2. File Structure

```text
mymud/
└── world/
    └── classes/
        ├── __init__.py
        ├── definitions.py   # The "Database" of classes (Warriors, Mages, etc.)
        ├── skills.py        # The "Database" of all abilities (Class & Universal)
        └── handler.py       # The ClassHandler logic engine
```

## 3. Data Definitions

### 3.1. `world/classes/definitions.py`

This file acts as the immutable registry of all available classes.

```python
CLASSES = {
    "warrior": {
        "name": "Warrior",
        "desc": "A master of arms and armor.",
        "xp_table": [0, 100, 300, 650, 1200],  # XP needed for Level 1, 2, 3...
        "abilities": {
            1: "slash",
            5: "power_strike",
            10: "warcry"
        },
        # Stats are applied using evennia.contrib.rpg.traits
        "traits": {
            "hp": {"base": 100, "type": "gauge"},
            "str": {"base": 10, "type": "static"},
            "mag": {"base": 5, "type": "static"}
        }
    },
    # ... other classes
}
```

### 3.2. `world/classes/skills.py`

A centralized dictionary for every skill in the game, preventing hardcoded strings in logic files.

```python
SKILLS = {
    "slash": {
        "name": "Slash",
        "desc": "A basic melee attack.",
        "type": "class", # vs "universal"
        "class_req": "warrior"
    },
    "sprint": {
        "name": "Sprint",
        "type": "universal"
    }
}
```

## 4. The Logic Engine: `ClassHandler`

Located in `world/classes/handler.py`. This handler manages the complexity of Main vs. Sub classes.

### 4.1. Storage Schema (On Character)
The character's `db` attributes will store:
*   `db.class_data`: A dictionary tracking progress *and* known skills for every unlocked class.
    ```python
    {
        "warrior": {
            "level": 5, 
            "xp": 450, 
            "known_skills": ["slash", "block"] # Only skills in this list are usable
        },
        "mage": {
            "level": 1, 
            "xp": 0, 
            "known_skills": ["magic_missile"]
        }
    }
    ```
*   `db.main_class`: String key (e.g., "warrior").
*   `db.sub_class`: String key (e.g., "mage") or `None`.

### 4.2. Key Methods

#### `set_job(main_class, sub_class=None)`
*   Validates that the character has unlocked these classes.
*   Updates `db.main_class` and `db.sub_class`.
*   Triggers a re-calculation of current stats/abilities.

#### `get_level(class_key)`
*   Returns the stored level from `db.class_data`.

#### `get_effective_level(class_key)`
*   **Crucial Logic:**
    *   If `class_key` == `main_class`: Return actual level.
    *   If `class_key` == `sub_class`: Return `min(actual_level, main_class_level / 2)`.
    *   Else: Return 0.

#### `gain_xp(amount)`
*   Applies *only* to the `main_class`.
*   Checks `xp_table` to see if a level-up occurs.

### 4.3 Integration with `contrib.rpg.traits`
While XP and Level are stored as simple numbers in `db.class_data`, the character's **Attributes** (Strength, Magic) and **Vitals** (HP, MP) will be managed by `TraitHandler`.
*   **On Job Change/Level Up:** The `ClassHandler` recalculates the base values for these traits.
    *   *Formula:* `Class Base + (Level * Growth Factor)`
*   **Benefits:** Traits automatically handle current/max values for HP/MP and allow for temporary modifiers (buffs/debuffs) without altering the base class stats.

#### `get_all_abilities()`
*   **Main Class:**
    1.  Get `known_skills` list from `db.class_data`.
    2.  Filter: Keep only skills where `req_level <= current_level`.
*   **Sub Class:**
    1.  Get `known_skills` list from `db.class_data`.
    2.  Calculate `effective_level` = `min(actual_sub_level, main_level / 2)`.
    3.  Filter: Keep only skills where `req_level <= effective_level`.
*   **Universal:** Add all skills from `db.universal_skills`.
*   **Return:** A unified list of distinct skill keys.

## 5. Integration with Character (`typeclasses/characters.py`)

The Character class remains lightweight, delegating all work to the handler.

```python
from world.classes.handler import ClassHandler

class Character(DefaultCharacter):
    def at_object_creation(self):
        self.class_handler = ClassHandler(self)
        
    def at_init(self):
        self.class_handler = ClassHandler(self)
```

## 6. Implementation Strategy

1.  **Phase 1: Structure:** Create the directories and the `definitions.py` / `skills.py` files with dummy data.
2.  **Phase 2: Handler:** Write the `ClassHandler` with `set_job` and XP logic.
3.  **Phase 3: Integration:** Hook it into `Character` and write a basic `level` command to test it.
4.  **Phase 4: Sub-Job Logic:** Implement the `get_effective_level` math and test the level caps.
