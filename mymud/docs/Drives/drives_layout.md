# Drives System Implementation Layout

This document details the architectural breakdown for implementing the "Drives" system in TessMUD. The revised design leverages **Evennia's native `contrib.rpg.traits`** module to handle numeric progression (Feelings and Focuses) and a simplified **Handler pattern** for logic.

## 1. Core Architecture

The system relies on three main components:
1.  **`contrib.rpg.traits.TraitHandler`**: Native Evennia component to manage the "Feeling" (0-100) and "Focus" (0-50) progress bars.
2.  **`DriveHandler`**: A lightweight custom handler attached to the `Character` typeclass. It acts as the interface between game events and the Trait system.
3.  **`DrivePrototype` (Script/Class)**: Definitions for the realized Drives (e.g., *Fear of Rats*), acting as passive "buffs" or modifiers.

## 2. File Structure

```text
mymud/
└── world/
    └── drives/
        ├── __init__.py
        ├── handler.py       # DriveHandler logic
        ├── data.py          # Configuration: Drive blueprints, mapping rules
        └── effects.py       # Definitions of realized Drives (Buffs/Modifiers)
```

## 3. Data Storage: `contrib.rpg.traits`

We will add the `TraitHandler` to the Character typeclass. This natively handles min/max values, current values, and types (Gauges vs. Counters).

### 3.1. Trait Configuration
*   **Feelings (The 4 Categories):** Implemented as **Gauge** traits (0 to 100).
    *   Keys: `drive_fear`, `drive_obsession`, `drive_resentment`, `drive_yearning`.
    *   Regeneration: None (only event-driven).
*   **Focuses (The Subjects):** Implemented as dynamic **Counter** traits (0 to 100).
    *   Keys: `focus_vermin`, `focus_fire`, `focus_blood`, etc.
    *   Created on-the-fly when a character first interacts with a subject.

## 4. The Logic Engine: `handler.py`

The `DriveHandler` abstracts the complexity of `traits`. It exposes high-level methods to the rest of the codebase.

**Note:** The specific triggers below (e.g., 'combat_flee' causing Fear) are **provisional examples**. The system is designed to be flexible so we can tune *what* causes feelings to rise later.

```python
# world/drives/handler.py

class DriveHandler:
    def __init__(self, obj):
        self.obj = obj  # The Character
        
    def register_event(self, event_type, target=None, **kwargs):
        """
        Main entry point for game events.
        
        Args:
            event_type (str): 'combat_flee', 'damage_taken', 'interaction', etc.
            target (Object): The object being interacted with (optional).
            kwargs: Extra data (amount of damage, etc).
        """
        # 1. Update Feelings (Fixed categories)
        if event_type == "combat_flee":
            self.obj.traits.drive_fear.add(5)
        elif event_type == "damage_taken":
            # Add Resentment scaled by damage?
            dmg = kwargs.get("damage", 1)
            self.obj.traits.drive_resentment.add(dmg)

        # 2. Update Focuses (Dynamic subjects via Tags)
        if target:
            # Check for special 'drive_focus' tags on the target
            # Convention: Tag category="drive_focus", Key="vermin"
            focus_tags = target.tags.get(category="drive_focus", return_list=True)
            
            for tag in focus_tags:
                trait_key = f"focus_{tag}"
                
                # Dynamic Trait Creation
                if trait_key not in self.obj.traits.all:
                     self.obj.traits.add(trait_key, "Counter", min=0, max=100)
                
                # Add progress
                self.obj.traits[trait_key].add(1)
```

## 5. Configuration: `data.py`

Maps combinations of Feelings and Focuses to specific Drive definitions.

```python
# world/drives/data.py

# (Feeling Key, Focus Key) -> Drive Definition
DRIVE_RECIPES = {
    ("drive_fear", "focus_fire"): "DRIVE_PYROPHOBIA",
    ("drive_obsession", "focus_vermin"): "DRIVE_RAT_KING",
}

# Definitions could be simple dicts or classes in effects.py
DRIVE_DEFINITIONS = {
    "DRIVE_PYROPHOBIA": {
        "name": "Fear of Fire",
        "description": "Flames dance in your nightmares.",
        "modifiers": {"bravery": -2},
        "xp_trigger": "flee_fire"
    }
}
```

## 6. Realization Logic (The Check)

When should the system check for a new Drive? Typically during a **Rest** or **Sleep** command.

```python
# In a 'Rest' command or script
def perform_drive_check(character):
    handler = character.drives
    traits = character.traits

    # 1. Identify Maxed Feelings
    maxed_feelings = [t for t in ['drive_fear', 'drive_obsession', ...] 
                      if traits[t].current >= 100]

    # 2. Identify Maxed Focuses
    maxed_focuses = [t for t in traits.all if t.startswith('focus_') 
                     and traits[t].current >= 100]

    # 3. Match
    for feeling in maxed_feelings:
        for focus in maxed_focuses:
            # Check recipes
            recipe = DRIVE_RECIPES.get((feeling, focus))
            if recipe:
                # 4. Award Drive (Implementation TBD: Buff or Attribute List)
                character.msg(f"You have developed a {recipe}!")
                # Reset bars?
                traits[feeling].reset()
                traits[focus].reset()
```

## 7. Integration Points

Instead of complex hooks, we use standard Evennia patterns:

1.  **`typeclasses/characters.py`**:
    *   Add `TraitHandler` to `at_object_creation`.
    *   Add `DriveHandler` as a property (lazy loaded).
2.  **`typeclasses/objects.py` (and children)**:
    *   Designers/Builders simply add Tags: `obj.tags.add("vermin", category="drive_focus")`.
3.  **Command Execution**:
    *   `Flee`: Call `caller.drives.register_event("combat_flee")`.
    *   `Attack`: Call `caller.drives.register_event("attack", target=target)`.

## 8. Summary of Benefits
*   **Less Code**: `contrib.rpg.traits` handles all the math, clamping, and validation.
*   **Flexible**: New "Focuses" are just new Tags. No code changes needed to add "Focus: Gold" or "Focus: Swords".
*   **Native**: Uses standard Tags and Attributes, making it compatible with other Evennia systems.