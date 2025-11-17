# Comprehensive Guide to Evennia Batch Building (`.ev`)

> **Purpose:** To provide a complete guide for human and AI builders on how to create complex and interactive MUD zones using Evennia's batch-command files (`.ev`). This document covers all features demonstrated in the official Evennia Tutorial World, from basic room construction to interactive objects, puzzles, and AI mobs.

---

## 1. Feature Checklist & Capabilities

This guide provides instructions for implementing the following features using `.ev` files. This list can be used to track the success and failure of AI-driven zone generation.

### Core Building & Structure
- [ ] **Four-Phase Build Pattern:** A strict, reliable sequence (Create, Describe, Decorate, Link) for error-free zone construction.
- [ ] **Room Creation:** Standard rooms with descriptions and aliases.
- [ ] **Two-Way Exits:** Linking rooms with standard directional commands.
- [ ] **Decorative Objects:** Creating and placing static, non-interactive props.
- [ ] **Locking Objects:** Preventing players from picking up scenery (`@lock get:false()`).

### Interactive Scenery & Puzzles
- [ ] **Room Details:** Adding non-object "look targets" to a room (e.g., `look wall`).
- [ ] **Readable Objects:** Items with text that can be read by players.
- [ ] **Climbable Objects:** Scenery that reveals hidden exits or information when climbed.
- [ ] **Conditional/Hidden Exits:** Exits that are only visible or usable after a condition is met (e.g., climbing an object).
- [ ] **Obelisk Puzzle:** An object that provides a random clue to the player, used to solve a later puzzle.
- [ ] **Teleport Puzzle Room:** A room that teleports the player to different destinations based on whether they have the correct clue from the Obelisk.
- [ ] **Crumbling Wall Puzzle:** An object that acts as a one-way exit after being interacted with multiple times.

### Advanced Room Types
- [ ] **Weather Rooms:** Rooms that automatically emit atmospheric messages at random intervals.
- [ ] **Dark Rooms:** Rooms that are pitch black until a player brings or creates a light source.
- [ ] **Bridge Room:** A room that simulates a multi-step crossing with a risk of falling.

### Combat & AI
- [ ] **AI Mob (NPC):** Creating an autonomous NPC that patrols a multi-room area and attacks players.
- [ ] **Combat Weapons:** Creating weapons with basic combat stats (hit, damage, parry).
- [ ] **Weapon Rack:** An object that dispenses a single, randomized weapon to a player.

### Special Objects
- [ ] **Light Source:** An object that can be lit to illuminate a `DarkRoom`.

---

## 2. Core Concepts

### 2.1. Execution
Run a batch file from in-game as a privileged user:
```
@batchcommand path.to.file
```
- Use **dot notation** for the path (e.g., `world.my_zone`), not slashes.
- Do **not** include the `.ev` file extension.

### 2.2. Syntax Rules (Critical)
Every command line **must** be followed by a blank comment line (`#`). This is non-negotiable; without it, Evennia merges commands, and the build will fail.

**✅ Correct:**
```ev
@create/drop My Room:rooms.Room
#
@desc My Room = A test room.
#
```

### 2.3. Naming Conventions
The first name given to an object is its player-facing **Display Name**. Subsequent names, separated by semicolons (`;`), are builder **aliases**.

- **Format:** `@create/drop Display Name;alias1;alias2:typeclass.path`
- **Rooms/Exits:** Use natural, capitalized phrases (e.g., "The Grand Hall", "North").
- **Objects (Props):** Use a **singular noun without an article** (e.g., "Table", "Rusty Key"). The engine automatically adds "a" or "an". Naming an object "A Table" will result in players seeing "a A Table".
- **Aliases:** Use lowercase, unique, and descriptive slugs for easy targeting (e.g., `gh_table`, `zone1_r01`).

### 2.4. The Four-Phase Build Pattern
To prevent errors, builds **must** follow this sequence. Do not mix commands from different phases.

1.  **Phase 1: Create Rooms:** Create all room objects for the zone using `@create/drop`. Do not describe or link them yet. This is a stateless phase.
2.  **Phase 2: Describe Rooms:** Set the descriptions for all created rooms using `@desc`. This is also stateless.
3.  **Phase 3: Decorate Rooms:** Teleport (`@tel`) into each room and create/describe all objects, NPCs, and interactive elements within it. This phase is **stateful** (location matters).
4.  **Phase 4: Link Rooms:** Teleport (`@tel`) into each room and create all exits using `@open`. This phase is also **stateful**.

---

## 3. Core Commands Reference

| Command | Function | Example |
|---|---|---|
| `@create/drop` | Create an object and place it. | `@create/drop Table;tbl:objects.Object` |
| `@desc` | Describe an object. | `@desc Table = A sturdy oak table.` |
| `@set` | Assign an attribute to an object. | `@set Table/material = "Oak"` |
| `@lock` | Apply a restriction to an object. | `@lock Table = get:false()` |
| `@tel` | Teleport yourself to a location. | `@tel The Grand Hall` |
| `@open` | Create an exit in your current room. | `@open north;n = The North Wing` |
| `@detail` | Add a non-object look target. | `@detail wall = The walls are stone.`|
| `mobon` | Activate a created Mob AI. | `mobon Ghost` |

---

## 4. Implementation Guide: Tutorial World Features

This section details how to implement each feature from the Tutorial World. **All typeclass paths are relative to `evennia.contrib.tutorials`**.

### 4.1. Standard Rooms & Exits
- **Typeclass:** `tutorial_world.rooms.TutorialRoom` (or a child class)
- **Implementation:** Follow the Four-Phase pattern. Use unique aliases for every room to ensure reliable linking.

```ev
# --- PHASE 1: CREATE ROOMS ---
@create/drop The First Room;zone1_r01:tutorial_world.rooms.TutorialRoom
#
@create/drop The Second Room;zone1_r02:tutorial_world.rooms.TutorialRoom
#

# --- PHASE 2: DESCRIBE ROOMS ---
@desc The First Room = A room of beginnings.
#
@desc The Second Room = Another room.
#

# --- PHASE 4: LINK ROOMS ---
@tel The First Room
#
@open east;e = The Second Room
#
@tel The Second Room
#
@open west;w = The First Room
#
```

### 4.2. Weather Room
Adds ambient, random weather messages to the room.
- **Typeclass:** `tutorial_world.rooms.WeatherRoom`
- **Implementation:** Simply create the room with this typeclass. No special attributes are needed.

```ev
@create/drop Cliff by the Sea;cliff:tutorial_world.rooms.WeatherRoom
#
@desc Cliff by the Sea = A windy, rain-swept cliff.
#
```

### 4.3. Room Details
Adds non-object targets for the `look` command.
- **Command:** `@detail`
- **Implementation:** Use during the Decorate phase. The target can have aliases.

```ev
# --- PHASE 3: DECORATE ROOMS ---
@tel Cliff by the Sea
#
@detail sea;ocean;waves = The gray sea stretches to the horizon.
#
```

### 4.4. Readable Object
An object that can be read.
- **Typeclass:** `tutorial_world.objects.TutorialReadable`
- **Attribute:** `readable_text` (string) - The text to be displayed when read.
- **Implementation:** Create the object and set its text.

```ev
# --- PHASE 3: DECORATE ROOMS ---
@tel Cliff by the Sea
#
@create/drop Wooden Sign;sign:tutorial_world.objects.TutorialReadable
#
@lock sign = get:false()
#
@desc sign = A weathered wooden sign.
#
@set sign/readable_text = "|rWARNING - The bridge is not safe!|n"
#
```

### 4.5. Climbable Object & Conditional Exit
An object that, when climbed, sets a Tag on the player, making a hidden exit visible and usable.
- **Typeclass:** `tutorial_world.objects.TutorialClimbable`
- **Attribute:** `climb_text` (string) - The descriptive text shown upon climbing.
- **Lock:** The exit uses a `tag()` lock function to check for the Tag set by the climbable object.
- **Implementation:**
    1.  Create the climbable object and its description.
    2.  Create the exit in the same room.
    3.  Lock the exit to require the tag `tutorial_climbed_tree` in the category `tutorial_world`.

```ev
# --- PHASE 3: DECORATE ROOMS ---
@tel Cliff by the Sea
#
@create/drop Gnarled Tree;tree:tutorial_world.objects.TutorialClimbable
#
@lock tree = get:false()
#
@desc tree = An old, sturdy tree.
#
@set tree/climb_text = You climb the tree and spot a hidden path to the north.
#

# --- PHASE 4: LINK ROOMS ---
@tel Cliff by the Sea
#
@open northern path;north;n = Hidden Grove
#
@lock northern path = view:tag(tutorial_climbed_tree, tutorial_world);traverse:tag(tutorial_climbed_tree, tutorial_world)
#
```

### 4.6. Bridge Room
A single room that simulates a dangerous, multi-step crossing.
- **Typeclass:** `tutorial_world.rooms.BridgeRoom`
- **Attributes:**
    - `west_exit` (string): The alias/name of the room at the west end.
    - `east_exit` (string): The alias/name of the room at the east end.
    - `fall_exit` (string): The alias/name of the room to teleport to if the player falls.
- **Implementation:** Create the room and set the three exit attributes. Do not create standard `@open` exits leading from the bridge itself.

```ev
# --- PHASE 1: CREATE ROOMS ---
# ... (create cliff, gatehouse, and ledge rooms first) ...
@create/drop The Old Bridge;bridge:tutorial_world.rooms.BridgeRoom
#

# --- PHASE 2: DESCRIBE ROOMS ---
@desc The Old Bridge = A rickety bridge swaying in the wind.
#

# --- PHASE 3: DECORATE ROOMS ---
@tel The Old Bridge
#
@set here/west_exit = cliff
#
@set here/east_exit = gatehouse
#
@set here/fall_exit = ledge
#
```

### 4.7. Dark Room & Light Source
A room that is dark until a `LightSource` object is lit within it.
- **Room Typeclass:** `tutorial_world.rooms.DarkRoom`
- **Object Typeclass:** `tutorial_world.objects.LightSource`
- **Implementation:**
    1.  Create the `DarkRoom`. Its `@desc` is only shown when there is light.
    2.  Create a `LightSource` object. Players can `get` it and `light` it.

```ev
# --- PHASE 1: CREATE ROOMS ---
@create/drop Dark Cell;dark_cell:tutorial_world.rooms.DarkRoom
#
# --- PHASE 2: DESCRIBE ROOMS ---
@desc Dark Cell = The flickering light reveals a small, damp cell.
#
# --- PHASE 3: DECORATE ROOMS ---
@tel SomeOtherRoom
#
@create/drop Wooden Splinter;splinter:tutorial_world.objects.LightSource
#
@desc splinter = A long, dry shard of wood. It looks like it would burn easily.
#
```

### 4.8. Crumbling Wall Puzzle
An object that functions as a one-way exit after a player interacts with it enough times.
- **Typeclass:** `tutorial_world.objects.CrumblingWall`
- **Attribute:** `destination` (string): The alias/name of the room to exit to.
- **Implementation:** Create the object in its room and set its destination. The object handles its own descriptions and puzzle logic.

```ev
# --- PHASE 3: DECORATE ROOMS ---
@tel Dark Cell
#
@create/drop Root-Covered Wall;wall;roots:tutorial_world.objects.CrumblingWall
#
@lock wall = get:false()
#
@set wall/destination = Underground Passage
#
```

### 4.9. Obelisk & Teleport Room Puzzle
A two-part puzzle. The player `look`s at the Obelisk, which gives them a clue (by setting a Tag on them). They then enter an antechamber with multiple exits. Only the exit corresponding to their clue leads to the reward; the others are traps.

- **Part 1: The Obelisk**
    - **Typeclass:** `tutorial_world.objects.Obelisk`
    - **Attribute:** `puzzle_descs` (tuple of strings): A list of the clue descriptions to be shown randomly.
- **Part 2: The Teleporter Tombs**
    - **Typeclass:** `tutorial_world.rooms.TeleportRoom`
    - **Attributes:**
        - `puzzle_value` (integer): The ID of the clue this tomb corresponds to (0-indexed, matching the order in `puzzle_descs`).
        - `success_teleport_to` (string): Room alias to go to on success.
        - `failure_teleport_to` (string): Room alias to go to on failure.
        - `success_teleport_msg` (string): Message shown on success.
        - `failure_teleport_msg` (string): Message shown on failure.

**Implementation:**
```ev
# --- In Castle Corner Room ---
@create/drop Obelisk:tutorial_world.objects.Obelisk
#
@lock Obelisk = get:false()
#
@set Obelisk/puzzle_descs = ("Image of a blue bird.", "Image of a woman on a horse.")
#

# --- In Antechamber ---
# This is the CORRECT tomb for the first clue (index 0)
@dig Blue Bird Tomb;tomb1:tutorial_world.rooms.TeleportRoom
#
@tel tomb1
#
@set here/puzzle_value = 0
#
@set here/success_teleport_to = Treasure Room
#
@set here/failure_teleport_to = Dark Cell
#
@set here/success_teleport_msg = The way opens!
#
@set here/failure_teleport_msg = It's a trap! You fall into darkness.
#
@tel Antechamber
#

# This is the CORRECT tomb for the second clue (index 1)
@dig Horse Tomb;tomb2:tutorial_world.rooms.TeleportRoom
#
@tel tomb2
#
@set here/puzzle_value = 1
#
@set here/success_teleport_to = Treasure Room
#
@set here/failure_teleport_to = Dark Cell
#
# ... (and so on for other attributes) ...
@tel Antechamber
#
```

### 4.10. AI Mob (NPC)
An autonomous, patrolling, aggressive NPC.
- **Typeclass:** `tutorial_world.mob.Mob`
- **Key Command:** `mobon <target>` to activate the AI after creation.
- **Attributes (many, see `build.ev` for a full list):**
    - `patrolling` (bool): `True`
    - `aggressive` (bool): `True`
    - `hunting` (bool): `True`
    - `send_defeated_to` (string): Room alias to send defeated players to.
    - `desc_alive` / `desc_dead` (strings): Descriptions for its states.
    - `defeat_msg` / `death_msg` (strings): Messages for combat outcomes.
    - `irregular_msgs` (list of strings): Random emotes.
- **Implementation:**
    1.  Create the mob object.
    2.  Set its home location with `@sethome`.
    3.  Set its many descriptive and behavioral attributes.
    4.  Create a weapon for it and teleport it into the mob's inventory.
    5.  Activate it with `mobon`. The mob will automatically patrol between its home room and any adjacent, unlocked rooms.

```ev
# --- In Castle Corner (Mob's home room) ---
@create/drop Ghostly Apparition;ghost:tutorial_world.mob.Mob
#
@sethome ghost = Castle Corner
#
@lock ghost = get:false()
#
@set ghost/desc_alive = A swirling mist of pure malice.
#
@set ghost/send_defeated_to = Dark Cell
#
@set ghost/patrolling = True
#
@set ghost/aggressive = True
#
@set ghost/hunting = True
#
# ... (many other message attributes) ...
#
# Create its weapon and give it to the mob
@create Foggy Tentacles;tentacles:tutorial_world.objects.TutorialWeapon
#
@set tentacles/damage = 5
#
@tel/quiet tentacles = ghost
#
# Activate the mob's AI
mobon ghost
#
```

### 4.11. Weapons and Weapon Racks
- **Weapon Typeclass:** `tutorial_world.objects.TutorialWeapon`
    - **Attributes:** `hit` (float), `damage` (int), `parry` (float).
- **Weapon Rack Typeclass:** `tutorial_world.objects.TutorialWeaponRack`
    - **Attributes:**
        - `rack_id` (string): A unique ID to prevent players from taking more than one weapon.
        - `available_weapons` (list of strings): A list of prototype-keys for the weapons it can dispense.
        - `no_more_weapons_msg` (string): Message for when the player tries to take a second weapon.

**Implementation:**
```ev
# --- Create a weapon directly ---
@create/drop Rusty Sword;sword:tutorial_world.objects.TutorialWeapon
#
@set sword/damage = 3
#

# --- Create a weapon rack ---
@tel The Armory
#
@create/drop Weapon Barrel;barrel:tutorial_world.objects.TutorialWeaponRack
#
@lock barrel = get:false()
#
@set barrel/rack_id = "armory_barrel"
#
@set barrel/available_weapons = ["knife", "dagger", "sword"]
#
@set barrel/no_more_weapons_msg = You already took a weapon.
#
```
