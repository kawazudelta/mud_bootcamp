
# Evennia Batch-Build Guide (`.ev` files)

> **Purpose:** How to write and execute Evennia batch-command files (`.ev`) for rapid, reliable creation of rooms, exits, and objects. This guide enforces a strict four-phase build pattern, correct formatting, and clear **Display Name + Aliases** naming so what players see is polished while builders get stable handles.

---

## 1. Overview

A **batch-command file** is a plain-text list of Evennia commands executed in sequence as if entered by a builder.  
Comments begin with `#`. **Blank comment lines** (`#`) are **mandatory** after every command line—without them, Evennia merges consecutive commands into one.

### Run Command
Execute a batch file in-game as a superuser or builder:

```
@batchcommand path.to.file
```

**Notes:**
- Use **dot notation**, not slashes (`/`).
- Do **not** include the `.ev` extension.
- Example: `@batchcommand world.tutorial`

---

## 2. Formatting Rules (Critical)

Every command line must be followed by a blank comment line (`#`).

### ❌ Incorrect
```ev
@create/drop r_0_0:rooms.Room
@desc r_0_0 = A dim stone chamber.
```

### ✅ Correct
```ev
@create/drop r_0_0:rooms.Room
#
@desc r_0_0 = A dim stone chamber.
#
```

Also:
- Start sections with headers like `# --- PHASE 1: CREATE ROOMS ---`.
- Group logically: **CREATE → DESCRIBE → DECORATE → LINK**.

---

## 3. Naming: Display Name First, Then Aliases

When creating an object (rooms, props, NPCs, exits), **the first name before any semicolons is the player-facing display name**.  
After that, add **aliases** separated by `;` for builder handles and natural shorthand.

### Why
- The first name is what players will *see* (object `.key`).
- Subsequent aliases give you stable, easy-to-type identifiers and slugs for scripting/linking.

### Style Guide
- **Rooms:** Title Case, often with a definite article (e.g., “**The Vestibule**”).  
- **Objects:** A singular noun phrase without an article (e.g., "**Lamp**", "**Old Ledger**"). The game automatically adds `a` or `an` before the name. For example, a `Lamp` object will appear to players as `a Lamp`. Do not use plurals (like `Shelves`) or include articles (`A Lamp`).
- **Aliases:** 
  - a **slug** for builders (e.g., `la_vestibule`, `la_obj_lamp`)  
  - an intuitive shorthand (e.g., `vestibule`, `lamp`)  
- **Uniqueness:** Ensure slugs are unique in the zone to avoid ambiguous references.  
- **Consistency:** Prefer predictable slug prefixes (e.g., `la_` for Lantern Archive).

### Examples (Correct)
```ev
@create/drop The Vestibule;la_vestibule;vestibule:rooms.Room
#
@desc The Vestibule = Light spills across etched brass tiles.
#
@create/drop Lamp;la_obj_lamp;lamp:objects.Object
#
@desc Lamp = A heavy glass hood protects a steady flame.
#
```

---

## 4. The Four-Phase Build Pattern (Critical)

To avoid errors where descriptions or objects fail to apply correctly, batch files **must** follow this strict four-phase sequence. Do not mix commands from different phases.

### Phase 1: Create Rooms (Stateless)
Create all rooms for the zone using `@create/drop`. Do not describe, decorate, or link them yet.

### Phase 2: Describe Rooms (Stateless)
Describe all the rooms you just created using `@desc`. Because you are targeting them by name, your builder's location does not matter for this step.

### Phase 3: Decorate Rooms (Stateful)
Teleport (`@tel`) into each room one by one. Inside each room, use `@create/drop` to place and describe static objects and NPCs. This phase is **stateful**—your builder's location matters.

### Phase 4: Link Rooms (Stateful)
Teleport (`@tel`) into each room one by one. Inside each room, use `@open` to create exits to other rooms. This phase is also **stateful**.

> **Why this order?** Attempting to describe a room after your builder has teleported somewhere else (a common mistake when mixing phases) will cause the `@desc` command to fail silently for the intended room. Separating the process guarantees each command works as expected.

---

## 5. Core Commands

| Command | Description |
|----------|--------------|
| `@create/drop <Display Name>;<alias1>[;alias2]:<typeclass>` | Create and drop with display name + aliases. |
| `@desc <target> = <text>` | Set description (supports multiline). |
| `@set <target>/<attr> = <value>` | Assign attributes. |
| `@lock <target> = <lockstring>` | Restrict access/interaction. |
| `@alias <target> = alias1;alias2` | Add aliases later if needed. |
| `@tel <room>` | Teleport the builder (placement/linking). |
| `@open <exitname>[;alias] = <destination>` | Create an exit from current room to destination. |

**Avoid** `@dig` and `@tunnel` for automated builds—mixing creation and linking by location is brittle.

---

## 6. Example: 3×3 Zone Build (Four-Phase Pattern)

### 6.1 Phase 1: Create Rooms
```ev
# --- PHASE 1: CREATE ROOMS ---
@create/drop The Southern Corner;z1_r_0_0;southcorner:rooms.Room
#
@create/drop The Southern Walk;z1_r_1_0;southwalk:rooms.Room
#
@create/drop The Southern Grate;z1_r_2_0;southgrate:rooms.Room
#
@create/drop The Middle Conduit;z1_r_0_1;midconduit:rooms.Room
#
@create/drop The Central Junction;z1_r_1_1;junction:rooms.Room
#
@create/drop The Machine Hall;z1_r_2_1;machinehall:rooms.Room
#
@create/drop The Northern Vent;z1_r_0_2;northvent:rooms.Room
#
@create/drop The Northern Chalk;z1_r_1_2;northchalk:rooms.Room
#
@create/drop The Northern Plate;z1_r_2_2;northplate:rooms.Room
#
```

### 6.2 Phase 2: Describe Rooms
```ev
# --- PHASE 2: DESCRIBE ROOMS ---
@desc The Southern Corner = Blue guide-lines pulse faintly beneath worn brass tiles.
#
@desc The Southern Walk = The air smells faintly of ozone.
#
@desc The Southern Grate = A grated floor reveals glimmers of red dust below.
#
@desc The Middle Conduit = A humming conduit runs through the wall.
#
@desc The Central Junction = A faded stencil marks evacuation routes.
#
@desc The Machine Hall = Distant machinery clatters through the vents.
#
@desc The Northern Vent = Drafts whisper from a ceiling vent.
#
@desc The Northern Chalk = Chalk marks warn of surges ahead.
#
@desc The Northern Plate = The wall here is warm to the touch.
#
```

### 6.3 Phase 3: Decorate Rooms (Example)
```ev
# --- PHASE 3: DECORATE ROOMS ---
@tel The Central Junction
#
@create/drop Lamp;la_obj_lamp;lamp:objects.Object
#
@desc Lamp = A heavy glass hood protects a steady flame.
#
@lock Lamp = get:false()
#
```

### 6.4 Phase 4: Link Rooms
```ev
# --- PHASE 4: LINK EAST-WEST ---
@tel The Southern Corner
#
@open east;e = The Southern Walk
#
@tel The Southern Walk
#
@open west;w = The Southern Corner
#
# ... and so on for all other connections.
```

---

## 7. Minimal 2×2 (Correct Four-Phase Style)
```ev
# --- PHASE 1: CREATE ROOMS ---
@create/drop The Cold Floor;z2_r_0_0;coldfloor:rooms.Room
#
@create/drop The Pipe Run;z2_r_1_0;piperun:rooms.Room
#
@create/drop The Graffiti Wall;z2_r_0_1;graffiti:rooms.Room
#
@create/drop The Ozone Hall;z2_r_1_1;ozonehall:rooms.Room
#

# --- PHASE 2: DESCRIBE ROOMS ---
@desc The Cold Floor = A metal floor hums beneath your boots.
#
@desc The Pipe Run = Condensation drips from overhead pipes.
#
@desc The Graffiti Wall = Spray paint shimmers in low light.
#
@desc The Ozone Hall = The air smells faintly of ozone.
#

# --- PHASE 4: LINK ROOMS --- (Phase 3 Decorate is skipped for this minimal example)
@tel The Cold Floor
#
@open east;e = The Pipe Run
#
@open north;n = The Graffiti Wall
#
@tel The Pipe Run
#
@open west;w = The Cold Floor
#
@open north;n = The Ozone Hall
#
@tel The Graffiti Wall
#
@open south;s = The Cold Floor
#
@open east;e = The Ozone Hall
#
@tel The Ozone Hall
#
@open south;s = The Pipe Run
#
@open west;w = The Graffiti Wall
#
```

---

## 8. Validation Checklist

- All rooms are created before any are described.
- All rooms are described before any objects are placed.
- All objects are placed before any exits are created.
- North then south returns you to origin; east then west returns you to origin.
- Rooms are reachable and names read well to players.
- Objects/NPCs appear in the correct rooms; not in inventory.

---

## 9. References

- **Batch-command Processor:**  
  https://www.evennia.com/docs/latest/Components/Batch-Command-Processor.html
- **Building Commands:**  
  https://www.evennia.com/docs/latest/api/evennia.commands.default.building.html

---

## 10. Proven Capabilities (Verified by Test Runs)

The following features have been **successfully executed** by an AI agent using this guide and validated in-game:

- **Create & describe rooms** using the strict four-phase build process.
- **Create & describe static (uninteractive) objects** using `@create/drop` and `@desc` during the Decorate phase.
- **Place content deterministically** by `@tel` to the target room before `@create/drop`.
- **Link rooms with two-way connections** using `@tel` + `@open` for each direction.
- **Lock down decorative props** with `@lock <object> = get:false()`.
- **Separator rule adherence**: Each command line is followed by a blank comment line `#`.

