# Builder Feature Request Log

> **Note:** This document tracks feature requests from the AI Builder cohort.
> **Format:** Requestor Persona, Concept, Implementation Sketch, Priority.

---

## Dependency Assessment & Implementation Roadmap

Based on technical analysis, the implementation order is prioritized to handle dependencies first (e.g., you can't have a vendor without currency, or loot chests without a loot table).

### Phase 1: Core Systems (The Backbone)
1.  **Random Loot Tables** (Fargo)
    *   *Dependency:* None.
    *   *Why:* Backend system needed by Containers (Loot Chests) and potentially Breakables.
2.  **Economy & Value Attributes** (Edinburgh - Component of Vendor System)
    *   *Dependency:* None.
    *   *Action:* Add `db.gold` to Characters and `value` field to Object Prototypes.
    *   *Why:* Prerequisite for the Vendor System.

### Phase 2: Interactive Objects (The Verbs)
3.  **Readable Objects** (Gundvagen)
    *   *Dependency:* None.
    *   *Why:* Base class for "Things with Text"; Prerequisite for Lore Tag integration.
4.  **Containers** (Byblos)
    *   *Dependency:* None (Logic-wise).
    *   *Why:* Essential for inventory management before item count grows too high.
5.  **Breakable Props** (Fargo)
    *   *Dependency:* Optional link to Loot Tables.

### Phase 3: Advanced Logic (The Gameplay)
6.  **Lore Tag System** (Adelaide)
    *   *Dependency:* Readable Objects (for the "Reading grants Lore" feature).
7.  **Simple Vendor System** (Edinburgh)
    *   *Dependency:* Economy Basics.
8.  **Triggers & Receivers** (Dalian)
    *   *Dependency:* None.

### Phase 4: Atmosphere & Exploration (The Polish)
9.  **Atmosphere Scripts** (Gundvagen)
    *   *Dependency:* None.
10. **Variable Exits** (Cordoba)
    *   *Dependency:* None.

---

## Feature: Readable Objects (Inscribed Matter)

**Requestor:** Gundvagen
**Date:** November 30, 2025
**Priority:** High (Essential for narrative layering)

### 1. The Concept
Objects that contain text separate from their physical description. A note is "a crumpled piece of paper" (description), but it *contains* "Help me" (content).
This allows for:
- Books, scrolls, tablets.
- Graffiti, signs, epitaphs.
- Hidden instructions for puzzles.
- Poetry stanzas fragmented across a level.

### 2. The Use Case
*   **Player Action:** `look Sign` -> "A rusted metal sign."
*   **Player Action:** `read Sign` -> "DANGER: HIGH VOLTAGE."

### 3. Implementation Sketch (Python/Evennia)

**A. The Typeclass (`typeclasses/objects.py` or `typeclasses/readable.py`)**
Create a class `Readable` inheriting from `Object`.
*   **Attribute:** `db.readable_text` (String). Stores the message.
*   **Method:** `at_object_creation()` sets a default empty string.

**B. The Command (`commands/mycommands.py`)**
Create a command `CmdRead`.
*   **Syntax:** `read <obj>`
*   **Logic:**
    1.  Search for target object in room or inventory.
    2.  Check for `read` lock (default: `true`).
    3.  Check if object has `db.readable_text`.
    4.  If yes, return the text to the caller.
    5.  If no, return "There is nothing written on that."

**C. The CmdSet**
Add `CmdRead` to the `CharacterCmdSet` (or a `DefaultCmdSet`) so all players can use it.

**D. Batch Command Support**
Update `Evennia_Batch_Build_Guide_v4.md` to support setting this data.
*   *Method:* Use the `@set` command in the batch file.
*   *Example:* `@set Note/readable_text = "The code is 0451."`

### 4. Technical Constraints
*   **Python 3.12:** No specific issues expected.
*   **Evennia:** Uses standard `Command` and `Object` classes.

---

## Feature: Breakable Props

**Requestor:** Fargo
**Date:** November 30, 2025
**Priority:** Medium (Interactive environment)

### 1. The Concept
Props that can be destroyed by player action, changing the environment or removing an obstacle.

### 2. The Use Case
*   **Player Action:** `smash Crate`
*   **Result:** The crate object is deleted. An echo message plays: "You smash the crate into splinters!"
*   **Advanced:** A "Broken Crate" object replaces the original (swapping objects).

### 3. Implementation Sketch
**A. The Typeclass**
`Breakable` object.
*   **Attribute:** `db.hp` (Health).
*   **Attribute:** `db.break_message` (Echo text).
*   **Hook:** `at_break()` handling the deletion/replacement logic.

**B. The Command**
`CmdSmash` (or `CmdAttack` integration).

---

## Feature: Random Loot Tables

**Requestor:** Fargo
**Date:** November 30, 2025
**Priority:** Medium (Reward loop)

### 1. The Concept
A backend system to select random items from weighted lists. Can be hooked into *anything* (mobs, breakables, quest rewards).

### 2. The Use Case
*   **Input:** `LootHandler.roll("TRASH_TIER_1")`
*   **Process:** Rolls 1d100 against a weighted table.
*   **Output:** Returns prototype key (e.g., `testadv.prototypes.RUSTY_GEAR`).

### 3. Implementation Sketch
**A. The Module (`world/loot_tables.py`)**
Python dictionary defining tiers and drop rates.

**B. The Spawner Integration**
A helper function `spawn_loot(location, table_name)` that rolls the table and immediately calls `evennia.prototypes.spawner.spawn()` to drop the item in the target location.

---

## Feature: Atmosphere Scripts (Decoupled Echoes)

**Requestor:** Gundvagen
**Date:** November 30, 2025
**Priority:** Medium (Immersion)

### 1. The Concept
A script-based system to add atmospheric echoes to ANY object or room, replacing the rigid `EchoingRoom` inheritance model. Composition over Inheritance.

### 2. The Use Case
*   **Builder Action:** `@script The Old Well = typeclasses.scripts.AtmosphereScript`
*   **Builder Action:** `@set The Old Well/atmosphere_messages = ["A drop of water splashes.", "A cold wind moans."]`
*   **System:** Every X seconds, the well echoes a message to the room.

### 3. Implementation Sketch
**A. The Script (`typeclasses/scripts.py`)**
Create `AtmosphereScript`.
*   **Attribute:** `db.messages` (List of strings).
*   **Attribute:** `db.interval` (Seconds).
*   **Method:** `at_repeat()` -> Picks a random message and sends it to `self.obj.location.msg_contents()` (if obj is an item) or `self.obj.msg_contents()` (if obj is a room).

**B. Migration**
Deprecate `EchoingRoom` in favor of standard `TestAdvRoom` + Script.

---

## Feature: Simple Vendor System (MVV)

**Requestor:** Edinburgh
**Date:** November 30, 2025
**Priority:** High (Economic Baseline)

### 1. The Concept
A minimalist "Infinite Stock" vendor that spawns items on purchase and destroys items on sale, using a simple `db.gold` integer on the player.

### 2. The Use Case
*   **Player Action:** `list` -> Shows wares and prices.
*   **Player Action:** `buy sword` -> Deducts gold, spawns sword.
*   **Player Action:** `sell potion` -> Destroys potion, adds gold.

### 3. Implementation Sketch
**A. The Typeclass (`typeclasses/npc.py` or `typeclasses/objects.py`)**
`Vendor` class.
*   **Attribute:** `db.wares` (Dict: `{"prototype_key": price}`).

**B. The Command Set (`commands/commerce.py`)**
`CommerceCmdSet` containing `CmdList`, `CmdBuy`, `CmdSell`.
*   **CmdBuy:** Validates gold -> Calls Spawner -> Deducts Gold.
*   **CmdSell:** Validates Item -> Deletes Item -> Adds Gold (50% value).

**C. Economy Basics**
*   Add `db.gold` (default 0) to `Character` typeclass.
*   Update Prototypes to include a `value` field for sell-back logic.

---

## Feature: Lore Tag System

**Requestor:** Adelaide
**Date:** November 30, 2025
**Priority:** Medium (Narrative Depth)

### 1. The Concept
A system to display extra information on `look` commands based on the character's possession of specific "Lore Tags."

### 2. The Use Case
*   **Player Status:** Has tag `lore_ancient_history`.
*   **Object:** Statue with `db.lore_req = "lore_ancient_history"` and `db.lore_text = "This is King Alaric."`
*   **Player Action:** `look Statue`
*   **Output:** "A weathered stone statue. [LORE: This is King Alaric.]"

### 3. Implementation Sketch
**A. The Tags (`typeclasses/characters.py`)**
Use Evennia's built-in `Tag` handler on the Character. `char.tags.add("lore_ancient_history", category="lore")`.

**B. The Object Hook (`typeclasses/objects.py`)**
Override `return_appearance` (or `get_display_desc`).
*   Check if `self.db.lore_req` exists.
*   Check if `looker.tags.get(self.db.lore_req, category="lore")`.
*   If Match: Append `self.db.lore_text` to the description.

**C. Integration with Readable Objects**
Update `CmdRead` (from Gundvagen's request) to optionally grant a tag upon reading.
*   Attribute: `db.grant_lore_tag`.

---

## Feature: Containers (Inventory Management)

**Requestor:** Byblos
**Date:** November 30, 2025
**Priority:** High (Inventory Hygiene)

### 1. The Concept
Objects that can hold other objects, reducing inventory clutter and allowing for "loot chests."

### 2. The Use Case
*   **Player Action:** `open Chest`
*   **Player Action:** `put Sword in Chest`
*   **Player Action:** `get Potion from Chest`
*   **Player Action:** `close Chest`
*   **Logic:** Items inside a closed container are hidden from the room/inventory list.

### 3. Implementation Sketch
**A. The Typeclass (`typeclasses/objects.py`)**
`Container` class.
*   **Attribute:** `db.capacity` (Max items or weight).
*   **Lock:** `open:false()` (Is it locked?).
*   **State:** `db.is_open` (Boolean).

**B. The Commands**
*   `open <obj>` / `close <obj>`: Toggles state.
*   `put <obj> in <container>`: Moves object to container's contents.
*   `get <obj> from <container>`: Moves object to player's contents.
*   **Note:** Evennia default commands may already handle `get/drop`. We need to ensure `put` and nested inventory visibility work correctly (i.e., you can't see inside a closed bag).

---

## Feature: Variable Exits (Shifting Paths)

**Requestor:** Cordoba
**Date:** November 30, 2025
**Priority:** Low (Advanced Exploration)

### 1. The Concept
Exits that do not lead to a single, static destination, but choose a destination from a list based on probability or state.

### 2. The Use Case
*   **Builder Setup:** Exit `North` has destinations `[Room A, Room B, Room C]`.
*   **Player Action:** `north`
*   **System:** Rolls random choice. Teleports player to `Room B`.

### 3. Implementation Sketch
**A. The Typeclass (`typeclasses/exits.py`)**
`VariableExit` class.
*   **Attribute:** `db.destinations` (List of dbrefs or aliases).
*   **Method:** Override `at_traverse(traversing_object, target_location)`.
    *   Instead of using `self.destination`, pick a random target from `db.destinations`.
    *   Execute traversal to that target.

**B. Integration with Batch Process**
*   Need a way to define multiple destinations in `.ev` files (likely via `@set`).

---

## Feature: Triggers & Receivers (Basic Machinery)

**Requestor:** Dalian
**Date:** November 30, 2025
**Priority:** Medium (Puzzle Logic)

### 1. The Concept
A rudimentary logic system where one object (Trigger) can send a signal to change the state of another object (Receiver).

### 2. The Use Case
*   **Player Action:** `pull Lever`
*   **System:** Lever checks `db.target` -> Finds `Gate`. Calls `Gate.trigger()`.
*   **Result:** Gate opens. Echo: "A heavy grinding sound is heard."

### 3. Implementation Sketch
**A. The Trigger Class (`typeclasses/objects.py`)**
`Trigger` class.
*   **Attribute:** `db.target` (dbref of receiver).
*   **Command:** `CmdPull` or `CmdPress`.

**B. The Receiver Interface**
*   Any object can be a receiver if it has an `at_trigger(source_obj)` method.
*   Example: `Gate` object toggles `db.is_locked` and `db.is_open` when triggered.

**C. Linking**
*   Need a way to link them. `@link_trigger <trigger> = <receiver>` builder command.