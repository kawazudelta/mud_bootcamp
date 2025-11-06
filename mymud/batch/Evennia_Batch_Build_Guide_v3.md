
# Evennia Batch-Build Guide (`.ev` files)

> **Purpose:** How to write and execute Evennia batch-command files (`.ev`) for rapid, reliable creation of rooms, exits, and objects. This guide enforces correct formatting, **`@create/drop` placement**, and clear **Display Name + Aliases** naming so what players see is polished while builders get stable handles.

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
- Start sections with headers like `# --- CREATE ROOMS ---`.
- Group logically: CREATE → DECORATE → LINK → CONTENTS.

---

## 3. Naming: Display Name First, Then Aliases

When creating an object (rooms, props, NPCs, exits), **the first name before any semicolons is the player-facing display name**.  
After that, add **aliases** separated by `;` for builder handles and natural shorthand.

### Why
- The first name is what players will *see* (object `.key`).
- Subsequent aliases give you stable, easy-to-type identifiers and slugs for scripting/linking.

### Style Guide
- **Rooms:** Title Case, often with a definite article (e.g., “**The Vestibule**”).  
- **Objects:** Natural English noun phrase (e.g., “**A Lamp**”, “**An Old Ledger**”).  
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
@create/drop A Lamp;la_obj_lamp;lamp:objects.Object
#
@desc A Lamp = A heavy glass hood protects a steady flame.
#
```

### Examples (Incorrect)
```ev
@create/drop la_vestibule:rooms.Room           # wrong: slug shown to players
#
@create/drop la_obj_lamp:objects.Object         # wrong: slug shown to players
#
```

> You can still add more aliases later with `@alias`. Prefer to supply the key and critical aliases at creation time for clarity.

---

## 4. Creation Placement Rule (`@create/drop`)

**Always use `@create/drop` in batch files.**

- Plain `@create` spawns the object **in your inventory**.
- `@create/drop` spawns it **in the current room** (for rooms: global space; for props/NPCs: visible in-place).
- For deterministic placement, `@tel` to the target room, then `@create/drop` there.

**Pattern**
```ev
@tel The Vestibule
#
@create/drop A Lamp;la_obj_lamp;lamp:objects.Object
#
@desc A Lamp = A heavy glass hood protects a steady flame.
#
```

---

## 5. Stateless vs. Stateful

- **Stateless phase**: `@tel` → `@create/drop` rooms/objects in their final rooms → `@desc`/`@set`/`@lock`.  
- **Stateful phase**: `@open` exits from inside each source room; `@tel` is required to move between rooms to create links.

---

## 6. Core Commands

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

## 7. Coordinate Conventions (2D Grid)

- **Axes:** `(x, y)` with `(0, 0)` at **south‑west** corner. (+x East, +y North)  
- **Room keys (aliases):** include a unique **slug alias** like `z1_r_2_1` for scripting, but keep the **display name** player-friendly.  
- **Directions:** `north (n)`, `east (e)`, `south (s)`, `west (w)`; diagonals optional.  
- **Traversal order:** Row‑major (south→north, west→east).

```text
(0,2)  (1,2)  (2,2)
(0,1)  (1,1)  (2,1)
(0,0)  (1,0)  (2,0)
```

---

## 8. Example: 3×3 Zone Build (Display Names + Aliases)

### 8.1 Create & Describe Rooms (Stateless via `@create/drop`)
```ev
# --- CREATE ROOMS ---
@create/drop The Southern Corner;z1_r_0_0;southcorner:rooms.Room
#
@desc The Southern Corner = Blue guide-lines pulse faintly beneath worn brass tiles.
#
@create/drop The Southern Walk;z1_r_1_0;southwalk:rooms.Room
#
@desc The Southern Walk = The air smells faintly of ozone.
#
@create/drop The Southern Grate;z1_r_2_0;southgrate:rooms.Room
#
@desc The Southern Grate = A grated floor reveals glimmers of red dust below.
#
@create/drop The Middle Conduit;z1_r_0_1;midconduit:rooms.Room
#
@desc The Middle Conduit = A humming conduit runs through the wall.
#
@create/drop The Central Junction;z1_r_1_1;junction:rooms.Room
#
@desc The Central Junction = A faded stencil marks evacuation routes.
#
@create/drop The Machine Hall;z1_r_2_1;machinehall:rooms.Room
#
@desc The Machine Hall = Distant machinery clatters through the vents.
#
@create/drop The Northern Vent;z1_r_0_2;northvent:rooms.Room
#
@desc The Northern Vent = Drafts whisper from a ceiling vent.
#
@create/drop The Northern Chalk;z1_r_1_2;northchalk:rooms.Room
#
@desc The Northern Chalk = Chalk marks warn of surges ahead.
#
@create/drop The Northern Plate;z1_r_2_2;northplate:rooms.Room
#
@desc The Northern Plate = The wall here is warm to the touch.
#
```

### 8.2 Link Rooms (Stateful with `@tel` + `@open`)
```ev
# --- LINK EAST-WEST ---
@tel The Southern Corner
#
@open east;e = The Southern Walk
#
@tel The Southern Walk
#
@open west;w = The Southern Corner
#
@open east;e = The Southern Grate
#
@tel The Southern Grate
#
@open west;w = The Southern Walk
#

@tel The Middle Conduit
#
@open east;e = The Central Junction
#
@tel The Central Junction
#
@open west;w = The Middle Conduit
#
@open east;e = The Machine Hall
#
@tel The Machine Hall
#
@open west;w = The Central Junction
#

@tel The Northern Vent
#
@open east;e = The Northern Chalk
#
@tel The Northern Chalk
#
@open west;w = The Northern Vent
#
@open east;e = The Northern Plate
#
@tel The Northern Plate
#
@open west;w = The Northern Chalk
#

# --- LINK NORTH-SOUTH ---
@tel The Southern Corner
#
@open north;n = The Middle Conduit
#
@tel The Middle Conduit
#
@open south;s = The Southern Corner
#
@open north;n = The Northern Vent
#
@tel The Northern Vent
#
@open south;s = The Middle Conduit
#

@tel The Southern Walk
#
@open north;n = The Central Junction
#
@tel The Central Junction
#
@open south;s = The Southern Walk
#
@open north;n = The Northern Chalk
#
@tel The Northern Chalk
#
@open south;s = The Central Junction
#

@tel The Southern Grate
#
@open north;n = The Machine Hall
#
@tel The Machine Hall
#
@open south;s = The Southern Grate
#
@open north;n = The Northern Plate
#
@tel The Northern Plate
#
@open south;s = The Machine Hall
#
```

---

## 9. Objects, NPCs, and Exits

### 9.1 Create Props in Place
```ev
@tel The Central Junction
#
@create/drop A Lamp;la_obj_lamp;lamp:objects.Object
#
@desc A Lamp = A heavy glass hood protects a steady flame.
#
@set  A Lamp/desc_detail = wick:A fine wick burns without smoke.
#
@lock A Lamp = get:false()
#
```

### 9.2 NPC (Simple)
```ev
@tel The Southern Walk
#
@create/drop An Attendant;la_npc_attendant;attendant:objects.Object
#
@desc An Attendant = A wary attendant in patchwork uniform.
#
@set  An Attendant/npc = true
#
@lock An Attendant = puppetable:true()
#
```

### 9.3 Flavor Exits
```ev
@tel The Central Junction
#
@open hatch;h = The Northern Chalk
#
@desc hatch = A circular hatch with a sticky wheel handle.
#
@alias hatch = up;u
#
```

---

## 10. Minimal 2×2 (Compact Style, Display Names First)
```ev
# --- CREATE ROOMS ---
@create/drop The Cold Floor;z2_r_0_0;coldfloor:rooms.Room
#
@desc The Cold Floor = A metal floor hums beneath your boots.
#
@create/drop The Pipe Run;z2_r_1_0;piperun:rooms.Room
#
@desc The Pipe Run = Condensation drips from overhead pipes.
#
@create/drop The Graffiti Wall;z2_r_0_1;graffiti:rooms.Room
#
@desc The Graffiti Wall = Spray paint shimmers in low light.
#
@create/drop The Ozone Hall;z2_r_1_1;ozonehall:rooms.Room
#
@desc The Ozone Hall = The air smells faintly of ozone.
#

# --- LINK ROOMS ---
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

## 11. Validation Checklist

- North then south returns you to origin; east then west returns you to origin.  
- All intended exits exist; none are duplicated.  
- Rooms are reachable and names read well to players.  
- Objects/NPCs appear in the correct rooms; not in inventory.  
- Locks/attributes behave as intended.  

---

## 12. References

- **Batch-command Processor:**  
  https://www.evennia.com/docs/latest/Components/Batch-Command-Processor.html
- **Building Commands:**  
  https://www.evennia.com/docs/latest/api/evennia.commands.default.building.html
- **Commands Overview:**  
  https://www.evennia.com/docs/latest/Components/Commands.html
- **Batch Processors Overview:**  
  https://www.evennia.com/docs/latest/Components/Batch-Processors.html
- **Running Evennia:**  
  https://www.evennia.com/docs/latest/Setup/Running-Evennia.html


---

## 13. Proven Capabilities (Verified by Test Runs)

The following features have been **successfully executed** by an AI agent using this guide and validated in-game:

- **Create & describe rooms** using `@create/drop <Display Name>;<aliases>:rooms.Room` followed by `@desc`.
- **Create & describe static (uninteractive) objects** using `@create/drop <Display Name>;<aliases>:objects.Object` followed by `@desc`.
- **Place content deterministically** by `@tel` to the target room before `@create/drop`.
- **Link rooms with two-way connections** using `@tel` + `@open` for each direction (N/E/S/W) and **directional aliases** (`n;e;s;w`) on exits.
- **Lock down decorative props** with `@lock <object> = get:false()` so players can’t pick them up.
- **Separator rule adherence**: Each command line is followed by a blank comment line `#` throughout the file.

> We will expand this list as additional features (e.g., exit descriptions, diagonal links, post-creation `@alias`, advanced `@set` attributes, `@move` staging flows) are tested and verified.
