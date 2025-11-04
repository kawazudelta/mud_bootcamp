
# Evennia Batch-Build Guide (`.ev` files)

> **Purpose:** This guide explains how to write and execute Evennia batch-command files (`.ev`) for rapid creation of rooms, exits, and objects. It emphasizes correct formatting, stateless creation, and reliable linking for human builders or automated generation systems.

---

## 1. Overview

A **batch-command file** is a plain-text list of Evennia commands executed in sequence as if entered by a builder.  
Comments begin with `#`. Blank comment lines (`#`) are **mandatory** between commands—without them, Evennia merges consecutive lines into a single command.

### Run Command
To execute a batch file in-game as a superuser or builder:

```
@batchcommand path.to.file
```

**Notes:**
- Use **dot notation**, not slashes (`/`).
- Do **not** include the `.ev` extension.
- Example: `@batchcommand world.tutorial`

---

## 2. Formatting Rules

Every command line must be followed by an empty comment line (`#`).  
This is critical—without it, Evennia will interpret multiple lines as one long command.

### ❌ Incorrect
```ev
@create r_0_0:rooms.Room
@desc r_0_0 = A dim stone chamber.
@create r_0_1:rooms.Room
@desc r_0_1 = A brighter corridor.
```

### ✅ Correct
```ev
@create r_0_0:rooms.Room
#
@desc r_0_0 = A dim stone chamber.
#
@create r_0_1:rooms.Room
#
@desc r_0_1 = A brighter corridor.
#
```

### Additional Guidelines
- Begin major sections with a comment header (`# --- SECTION NAME ---`).
- Group commands logically: creation, decoration, linking, contents.
- Always use consistent indentation and naming.

---

## 3. Stateless Creation Methodology

To ensure deterministic, safe builds—especially when generated automatically—separate creation and linking into two phases.

### Phase 1: Create and Describe (Stateless)
You can create and describe rooms from anywhere without changing location.

### Phase 2: Connect (Stateful)
Connecting rooms requires being physically inside them. Use `@tel` to move between rooms when opening exits.

---

## 4. Core Commands

| Command | Description |
|----------|--------------|
| `@create <key>[:typeclass]` | Creates a room, object, or exit. |
| `@desc <target> = <text>` | Sets the description. |
| `@set <target>/<attr> = <value>` | Assigns attributes. |
| `@lock <target> = <lockstring>` | Restricts access. |
| `@alias <target> = name1;name2` | Adds command aliases. |
| `@tel <room>` | Teleports builder to a room (required for linking). |
| `@open <exitname>[;alias] = <destination>` | Creates an exit from current room to destination. |

**Avoid:**  
- `@dig` and `@tunnel` (combine creation and linking in one stateful command).  
  Use explicit `@create`, `@tel`, and `@open` instead.

---

## 5. Coordinate Conventions (2D Grid)

- **Axes:** `(x, y)` with `(0, 0)` at **south‑west** corner.  
  - +x = East, −x = West, +y = North, −y = South.  
- **Room keys:** `r_x_y` (e.g., `r_2_1`).  
- **Directions:** `north (n)`, `east (e)`, `south (s)`, `west (w)`  
  (optionally diagonals: `ne`, `nw`, `se`, `sw`).
- **Traversal order:** Row-major (south to north, west to east).

### Example Grid (3×3)

```text
(0,2)  (1,2)  (2,2)
(0,1)  (1,1)  (2,1)
(0,0)  (1,0)  (2,0)
```

---

## 6. Example: 3×3 Zone Build

### 6.1 Create Rooms (Stateless)
```ev
# --- CREATE ROOMS ---
@create r_0_0:rooms.Room
#
@desc r_0_0 = A square of cracked stone. Blue guide-lines pulse faintly underfoot.
#
@create r_1_0:rooms.Room
#
@desc r_1_0 = The air smells faintly of ozone.
#
@create r_2_0:rooms.Room
#
@desc r_2_0 = A grated floor reveals glimmers of red dust below.
#
@create r_0_1:rooms.Room
#
@desc r_0_1 = A humming conduit runs through the wall.
#
@create r_1_1:rooms.Room
#
@desc r_1_1 = A central junction marked with fading paint.
#
@create r_2_1:rooms.Room
#
@desc r_2_1 = You hear distant machinery through the vents.
#
@create r_0_2:rooms.Room
#
@desc r_0_2 = Drafts whisper from a ceiling vent.
#
@create r_1_2:rooms.Room
#
@desc r_1_2 = Chalk marks warn of power surges ahead.
#
@create r_2_2:rooms.Room
#
@desc r_2_2 = The wall here is warm to the touch.
#
```

### 6.2 Connect Rooms (Stateful)
Each `@open` must be executed from within the source room using `@tel`.

```ev
# --- LINK EAST-WEST ---
@tel r_0_0
#
@open east;e = r_1_0
#
@tel r_1_0
#
@open west;w = r_0_0
#
@open east;e = r_2_0
#
@tel r_2_0
#
@open west;w = r_1_0
#

@tel r_0_1
#
@open east;e = r_1_1
#
@tel r_1_1
#
@open west;w = r_0_1
#
@open east;e = r_2_1
#
@tel r_2_1
#
@open west;w = r_1_1
#

@tel r_0_2
#
@open east;e = r_1_2
#
@tel r_1_2
#
@open west;w = r_0_2
#
@open east;e = r_2_2
#
@tel r_2_2
#
@open west;w = r_1_2
#

# --- LINK NORTH-SOUTH ---
@tel r_0_0
#
@open north;n = r_0_1
#
@tel r_0_1
#
@open south;s = r_0_0
#
@open north;n = r_0_2
#
@tel r_0_2
#
@open south;s = r_0_1
#

@tel r_1_0
#
@open north;n = r_1_1
#
@tel r_1_1
#
@open south;s = r_1_0
#
@open north;n = r_1_2
#
@tel r_1_2
#
@open south;s = r_1_1
#

@tel r_2_0
#
@open north;n = r_2_1
#
@tel r_2_1
#
@open south;s = r_2_0
#
@open north;n = r_2_2
#
@tel r_2_2
#
@open south;s = r_2_1
#
```

---

## 7. Objects and Props

### Example: Stationary Object
```ev
@create o_console:objects.Object
#
@desc o_console = A scuffed maintenance console blinks sporadically.
#
@set o_console/desc_detail = panels:Loose panels reveal braided cables.
#
@tel r_1_1
#
@move o_console = here
#
@lock o_console = get:false()
#
```

### Example: Exit with Description
```ev
@tel r_1_1
#
@open hatch;h = r_1_2
#
@desc hatch = A circular hatch with a sticky wheel handle.
#
@alias hatch = up;u
#
```

### Example: NPC (Simple Object)
```ev
@create m_attendant:objects.Object
#
@desc m_attendant = A wary attendant in patchwork uniform.
#
@set m_attendant/npc = true
#
@tel r_1_0
#
@move m_attendant = here
#
```

---

## 8. Example: Minimal 2×2 Build (Compact Style)

```ev
# --- CREATE ROOMS ---
@create r_0_0:rooms.Room
#
@desc r_0_0 = A cold metal floor hums beneath your boots.
#
@create r_1_0:rooms.Room
#
@desc r_1_0 = Pipes run overhead, dripping condensation.
#
@create r_0_1:rooms.Room
#
@desc r_0_1 = Flickering lights reveal graffiti on the walls.
#
@create r_1_1:rooms.Room
#
@desc r_1_1 = The air smells faintly of ozone.
#

# --- LINK ROOMS ---
@tel r_0_0
#
@open east;e = r_1_0
#
@open north;n = r_0_1
#
@tel r_1_0
#
@open west;w = r_0_0
#
@open north;n = r_1_1
#
@tel r_0_1
#
@open south;s = r_0_0
#
@open east;e = r_1_1
#
@tel r_1_1
#
@open south;s = r_1_0
#
@open west;w = r_0_1
#
```

---

## 9. Authoring Tips for Reliability

- Always add a blank `#` line after each command.  
- Use globally unique keys (prefix with zone name if needed).  
- Group commands by purpose (CREATE, DECORATE, LINK, CONTENTS).  
- Avoid implicit movement (`@dig/tel` side effects).  
- Use comment maps for reference.

Example:
```ev
# (0,1) [r_0_1] — [r_1_1]
#   |        |
# (0,0) [r_0_0] — [r_1_0]
```

---

## 10. Validation Checklist

- Moving north then south returns you to start.  
- Moving east then west returns you to start.  
- All intended exits exist; none are duplicated.  
- Objects are placed correctly.  
- Locked items behave as intended.  
- All rooms are reachable.

---

## 11. References and Further Reading

- **Batch-command Processor Documentation:**  
  https://www.evennia.com/docs/latest/Components/Batch-Command-Processor.html

- **Building Command Reference:**  
  https://www.evennia.com/docs/latest/api/evennia.commands.default.building.html

- **General Command System Overview:**  
  https://www.evennia.com/docs/latest/Components/Commands.html

- **Batch Processors Overview:**  
  https://www.evennia.com/docs/latest/Components/Batch-Processors.html

- **Running Evennia:**  
  https://www.evennia.com/docs/latest/Setup/Running-Evennia.html
