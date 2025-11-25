# Drives System Implementation Layout

This document details the architectural breakdown and file structure for implementing the "Drives" system in TessMUD. It utilizes a **Handler pattern** combined with a **Semantic Event System** to track player behavior and object interactions.

## 1. File Structure

```text
mymud/
└── world/
    └── drives/
        ├── __init__.py
        ├── handler.py       # The logic engine attached to the Character
        ├── drive_data.py    # Configuration, Constants, and Rules Maps
        └── effects.py       # (Optional) Specific logic for unique drive effects
```

## 2. Data Structure (`drive_data.py`)

This file contains the "DNA" of the system: Constants, Blueprints, and the Rules Interaction Map.

### Core Constants & Blueprints
```python
# world/drives/drive_data.py

# --- Slots ---
SLOT_OBSESSION = "obsession"
SLOT_YEARNING = "yearning"
SLOT_RESENTMENT = "resentment"
SLOT_FEAR = "fear"

FEELINGS = {
    SLOT_OBSESSION: "Obsession",
    SLOT_YEARNING: "Yearning",
    SLOT_RESENTMENT: "Resentment",
    SLOT_FEAR: "Fear"
}

# --- Thresholds ---
FEELING_THRESHOLD = 100
FOCUS_THRESHOLD = 50

# --- Drive Blueprints ---
# Key format: (FEELING, FOCUS)
DRIVE_BLUEPRINTS = {
    (SLOT_FEAR, "fire"): {
        "name": "Fear of Fire",
        "desc": "Flames terrify you...",
        "bonuses": {"hp": 10},
        "xp_trigger": "flee_fire"
    },
    (SLOT_OBSESSION, "vermin"): {
        "name": "Obsession with Rats",
        "desc": "You see patterns in the scurrying...",
        "bonuses": {"perception": 2},
        "xp_trigger": "interact_vermin"
    }
}
```

### The Interaction Map (Semantic Events)
This dictionary maps **Semantic Event Keys** (not just commands) and **Tags** to Drive Points.

**Vocabulary of Events:**
*   `consume`: Eating or drinking.
*   `combat_kill`: Killing an entity.
*   `combat_flee`: Escaping combat.
*   `receive_damage`: Taking HP damage.
*   `inflict_status`: Causing a status effect (bleed, burn).
*   `manipulate`: Using, wielding, or lighting objects.

```python
# --- Interaction Rules ---
# Key: (EVENT_KEY, TAG) -> Value: (FOCUS_KEY, POINTS)
OBJECT_POINT_MAP = {
    # Vermin Interactions
    ("combat_kill", "vermin"): ("vermin", 5),
    ("consume", "vermin"):     ("vermin", 10),
    
    # Fire Interactions
    ("manipulate", "fire"):    ("fire", 1),   # e.g. lighting a torch
    ("inflict_status", "burn"):("fire", 3),   # e.g. causing a burn
    
    # Blood Interactions
    ("consume", "blood"):      ("blood", 2),
    ("inflict_status", "bleed"):("blood", 5), # "Spilling blood"
}
```

## 3. The Logic Engine (`handler.py`)

The **Handler** processes interactions using the semantic keys.

```python
# world/drives/handler.py
from world.drives import drive_data

class DriveHandler:
    # ... init ...

    def register_interaction(self, event, target=None, action_tags=None):
        """
        The Smart Trigger.
        Args:
            event (str): The semantic event key (e.g., 'combat_kill', 'receive_damage').
            target (Object, optional): The object being interacted with.
            action_tags (list, optional): Extra tags describing the action itself (e.g., ['fire']).
        """
        tags_to_check = []
        
        # 1. Get Tags from Target Object
        if target:
            tags_to_check.extend(target.tags.all()) 

        # 2. Add Action Tags
        if action_tags:
            tags_to_check.extend(action_tags)

        # 3. Process Logic
        for tag in tags_to_check:
            # Check for matches in the rules map
            rule = drive_data.OBJECT_POINT_MAP.get((event, tag))
            if rule:
                focus_key, amount = rule
                self.add_progress(focus_key=focus_key, amount=amount)

        # 4. Handle 'Feelings' based on Event Type
        if event == "combat_flee":
            self.add_progress(feeling_key=drive_data.SLOT_FEAR, amount=5)
        elif event == "receive_damage":
            # Amount based on actual damage could be passed in kwargs if needed
            self.add_progress(feeling_key=drive_data.SLOT_RESENTMENT, amount=1)
```

## 4. Expansion Procedure

### How to Add a New Focus (e.g., "Gold")
1.  **Update `drive_data.py`:**
    *   Add constant: `FOCUS_GOLD = "gold"`
    *   Add entries to `OBJECT_POINT_MAP`: `("manipulate", "coin"): ("gold", 1)`
    *   Add `DRIVE_BLUEPRINTS`: `(SLOT_OBSESSION, FOCUS_GOLD): {...}`
2.  **Tag Game Objects:**
    *   Ensure coins, treasure chests, etc., have the tag `coin`.
    *   *No code changes required in the engine.*

### How to Add a New Trigger (e.g., "Stealing")
1.  **Identify the Hook:** Find the `steal` command code or the `at_object_receive` hook.
2.  **Insert the Call:**
    ```python
    # In the steal command:
    caller.drives.register_interaction(event="theft", target=target_obj)
    ```
3.  **Update Rules:**
    *   Add `("theft", "gold"): ("gold", 10)` to `OBJECT_POINT_MAP` in `drive_data.py`.

## 5. Integration Points (Hooks)

*   **`at_damage` (Character):** Call `register_interaction("receive_damage", target=attacker)`.
*   **`at_object_creation` (Prototypes):** Ensure mobs/items have descriptive tags (`vermin`, `fire`, `blood`).
*   **Combat System:**
    *   On kill: `register_interaction("combat_kill", target=victim)`
    *   On status effect: `register_interaction("inflict_status", target=victim, action_tags=["bleed"])`
*   **Commands:**
    *   `eat`: `register_interaction("consume", target=obj)`
    *   `flee`: `register_interaction("combat_flee")`

## 6. Example Walkthrough: Obsession with Dragons

This plain-language example illustrates how the components work together to give a character an **Obsession with Dragons**.

### Phase 1: The Setup (Builder Work)
1.  **Tagging:** The builder creates a dragon NPC (e.g., "Smaug") and gives him the tag `"dragon"`.
2.  **Rule Definition:** In `drive_data.py`, a rule is added to `OBJECT_POINT_MAP`:
    *   `("observe", "dragon"): ("dragon", 1)` (Looking at dragons gives Dragon Points).

### Phase 2: Player Actions
1.  **Interaction:** The player types `look at smaug`.
2.  **System Trigger:**
    *   The code registers an **"observe"** event on a target with the **"dragon"** tag.
    *   The Handler looks up the rule and adds +1 to the character's **Dragon Focus** bar.
3.  **Building Obsession:**
    *   Repeated non-hostile interactions (reading dragon books, talking to dragons) accumulate "Intensity" points, which fill the **Obsession Feeling** bar.

### Phase 3: The Tipping Point
*   **Focus Bar:** Reaches 50 "Dragon Points."
*   **Feeling Bar:** Reaches 100 "Obsession Points."
*   The Drive is now fully formed but sits in a "Pending" state.

### Phase 4: The Reveal (Resting)
1.  **Command:** The player types `rest`.
2.  **Processing:** The Handler checks for pending drives. It sees **Max Obsession** + **Max Dragon Focus**.
3.  **Result:** The player receives a message: *"Your dreams are filled with scales and smoke."*
4.  **Equip:** **Obsession with Dragons** is automatically equipped in the Obsession slot.

### Phase 5: The Effect
The player now has a permanent drive that might grant:
*   **Bonus:** +2 Intelligence when in the same room as a dragon.
*   **XP Trigger:** Gain XP when discovering a new dragon species.