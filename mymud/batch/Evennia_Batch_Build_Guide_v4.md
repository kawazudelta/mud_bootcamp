## 1. Batch File Execution
---

### ✅ Features Verified in Live Testing

The following features have been successfully tested in Evennia using `.ev` batch files:

- Room creation using `@create/drop` with display-name-first naming and aliasing
- Room descriptions using `@desc`
- Teleportation using `@tel` to manage link state and placement
- Exit creation using `@open` with directional aliases (e.g. `north;n`)
- Two-way room linking using repeated `@tel` + `@open`
- Static object creation using `@create/drop`
- Descriptive objects using `@desc`
- Prop locking using `@lock get:false()` to prevent pickup
- Attribute-based object details using `@set desc_detail`
- Alias assignments at creation time using `;` (e.g., `@create/drop A Lamp;lamp1;la_lamp`)

This list expands as new features are verified in-world.

---


- Run a batch file using:
  ```
  @batchcommand path.to.file
  ```
- Use dot-notation (no slashes, no `.ev` extension).

---

## 2. Syntax Rules

- Every command **must be followed by** a blank comment line:
  ```
  @create/drop A Room;alias:rooms.Room
  #
  ```
- Do not insert actual blank lines. All spacers must be `#`.

---

## 3. Naming: Display Name First, Then Aliases

When creating an object (rooms, props, NPCs, exits), **the first name before any semicolons is the player-facing display name**.  
This is what players see in the game interface.  
Subsequent names, separated by semicolons, should be **aliases** for use by Builders and scripts. These can include zone slugs, shorthand labels, or internal references.

Use natural English phrases for the display name (e.g., “The Vault”, “A Rusty Sword”), and use lowercase, underscore-based identifiers for aliases (e.g., `la_vault`, `sword`, `z1_r_0_0`).

**Format:**  
```
@create/drop Display Name;alias1;alias2:typeclass
```

**Examples:**
```
@create/drop The West Wing;z0_r_0_0;west:rooms.Room
#
@create/drop A Metal Crate;crate_a;la_crate:objects.Object
#


- First name = display name (player-facing), in natural language
- Following names = aliases (for builder use, or command convenience)
- Format: `@create/drop Display Name;alias1;alias2:typeclass`

**Example:**
```
@create/drop The West Wing;z0_r_0_0;west:rooms.Room
#
```

---

## 4. Commands Overview

This is a list of all valid commands usable in `.ev` batch files. Each command must follow the strict batch format: one command per line followed by a blank comment line (`#`). These commands are interpreted as if a Builder typed them directly into the Evennia console.

Avoid `@dig` and `@tunnel` for AI/Builder-generated `.ev` files—they involve implicit teleporting and linking that cannot be easily scripted.

| Command      | Function                                 |
|--------------|------------------------------------------|
| `@create/drop` | Create and place object/room in current location |
| `@desc`      | Assign a description text to a target    |
| `@open`      | Create an exit from the current room     |
| `@tel`       | Move the Builder to a room before linking or dropping |
| `@lock`      | Apply permissions or visibility restrictions |
| `@set`       | Assign attributes (e.g., embedded details) |
| `@alias`     | Add alternative references to an object post-creation |
| `@move`      | Move an object from staging to its intended room |


| Command      | Function                                 |
|--------------|------------------------------------------|
| `@create/drop` | Create and drop object or room           |
| `@desc`      | Add description                          |
| `@open`      | Create directional exit                  |
| `@tel`       | Move to location                         |
| `@lock`      | Apply access control                     |
| `@set`       | Define attribute or desc_detail          |
| `@alias`     | Add aliases post-creation                |
| `@move`      | Move object to room                      |

Avoid: `@dig`, `@tunnel` — use explicit stateless creation and linking.

---

## 5. Rooms [Tested]

### Create and Describe

```
@create/drop The Generator Room;gen_room;z1_r_0_0:rooms.Room
#
@desc The Generator Room = A square metal room humming with energy.
#
```

---

## 6. Exits [Tested]

### Create Exit (One-way)
```
@tel The Generator Room
#
@open east;e = Control Room
#
```

### Create Two-way Link
```
@tel The Generator Room
#
@open east;e = Control Room
#
@tel Control Room
#
@open west;w = The Generator Room
#
```

**Directional aliases** (recommended): `north;n`, `south;s`, `east;e`, `west;w`

---

## 7. Objects [Tested]

### Create Decorative Prop

```
@tel The Generator Room
#
@create/drop A Console Panel;console_panel;panel:objects.Object
#
@desc A Console Panel = A flickering console with blinking lights.
#
@lock A Console Panel = get:false()
#
```

### Move to Target Room

```
@move A Console Panel = The Generator Room
#
```

---

## 8. Locking [Tested]

- Prevent interaction or access
```
@lock A Lamp = get:false()
#
@lock A Door = traverse:perm(Builder)
#
```

---

## 9. Descriptions [Tested]

### Standard Description

```
@desc The Bridge = A steel platform overlooking the reactor.
#
```

### Detail Description (desc_detail)

```
@set A Console/desc_detail = screen:A cracked green-glass screen.
#
```

---

## 14. Combined Example (Minimal Zone) [Tested]

```
@create/drop The South Hall;z0_r_0_0;southhall:rooms.Room
#
@desc The South Hall = A dimly lit brass corridor.
#
@create/drop The North Hall;z0_r_0_1;northhall:rooms.Room
#
@desc The North Hall = A vaulted room with green banners.
#
@tel The South Hall
#
@open north;n = The North Hall
#
@tel The North Hall
#
@open south;s = The South Hall
#
@tel The South Hall
#
@create/drop A Lamp;lamp1;la_lamp:objects.Object
#
@desc A Lamp = A sturdy oil lamp.
#
@lock A Lamp = get:false()
#
```

---

## 15. Glossary

| Command      | Example                                             | Purpose                             |
|--------------|-----------------------------------------------------|-------------------------------------|
| `@create/drop` | `@create/drop The Vault;vault:rooms.Room`         | Create and place                    |
| `@desc`      | `@desc The Vault = A sealed chamber.`               | Set description                     |
| `@open`      | `@open north;n = The North Room`                    | Create exit                         |
| `@tel`       | `@tel The Vault`                                    | Teleport                            |
| `@lock`      | `@lock A Lamp = get:false()`                        | Prevent pickup                      |
| `@alias`     | `@alias A Lamp = torch;lantern`                     | Add aliases                         |
| `@set`       | `@set A Box/detail = lid:A rusty lid`               | Add detail                          |
| `@move`      | `@move A Box = The Vault`                           | Move object                         |

---

## 16. Builder Execution Notes

- Every command must be followed by `#`
- Use dot-notation with `@batchcommand`
- No `.ev` extension in command
- Do not use `@dig`, `@tunnel`
- Objects created must use display-name-first + aliases

---


---



---

## 17. Untested Features from Tutorial World [Untested]

The following features come from Evennia's official tutorial world and demonstrate advanced gameplay mechanics. These examples show how to implement each feature using only `.ev` batch commands. Each example includes a short description so Builder agents can understand the design intent and logic behind the structure.

### Room Details via @detail
Use this to add special "look targets" to a room that are not physical objects. Players can `look wall` or `look ceiling`, for example.

```
@tel The Vestibule
#
@detail wall;walls = The ancient stone is etched with faded symbols.
#
```

### Conditional and Hidden Exits
Create exits that are not visible or usable unless a player meets a condition, like holding a specific key.

```
@tel The North Passage
#
@open secret passage;hidden = Secret Room
#
@lock secret passage = traverse: holds("silver key"); search: holds("silver key")
#
```

### Lightable Objects (LightSource)
Creates an item a player can "light" to illuminate a dark room. Burns out after a delay.

```
@tel The Vault
#
@create/drop A Wooden Splinter;splinter:evennia.contrib.tutorials.tutorial_world.objects.LightSource
#
@desc A Wooden Splinter = A long dry shard of wood. Could be lit as a torch.
#
```

### Climbable Object (TutorialClimbable)
Use this to simulate vertical movement. A player can `climb` the object to trigger an action.

```
@tel The Cell
#
@create/drop A Wine Rack;wine_rack:evennia.contrib.tutorials.tutorial_world.objects.TutorialClimbable
#
@desc A Wine Rack = A tall wooden rack that could be climbed.
#
```

### Stateful Obelisk (Randomized Detail)
Generates a random clue each time it's examined. Stores clue info on the player for use in puzzles.

```
@tel The Crypt Entry
#
@create/drop Obelisk of Trials;obelisk:evennia.contrib.tutorials.tutorial_world.objects.Obelisk
#
@desc Obelisk of Trials = A glowing stone that pulses with unseen power.
#
```

### Dark Room Mechanics (DarkRoom + LightSource)
Creates a room that appears pitch black unless a lit LightSource is present. Use together with Lightable objects.

```
@create/drop The Cell;dark_cell:evennia.contrib.tutorials.tutorial_world.rooms.DarkRoom
#
@desc The Cell = It's pitch black. You can't see anything.
#
```

### BridgeRoom with Fall Risk
Simulates a multi-step crossing in a single room. Player must issue repeated movement commands to cross safely.

```
@create/drop The Bridge;bridge_room:evennia.contrib.tutorials.tutorial_world.rooms.BridgeRoom
#
@desc The Bridge = A narrow crossing suspended above mist.
#
@set The Bridge/east_exit = Gate Room
@set The Bridge/west_exit = Cliffside
@set The Bridge/fall_exit = Ravine Floor
#
```

### WeatherRoom (Ambient Descriptions)
Automatically emits weather descriptions at intervals. Adds atmosphere to outdoor areas.

```
@create/drop Cliffside;weather_cliff:evennia.contrib.tutorials.tutorial_world.rooms.WeatherRoom
#
@desc Cliffside = You stand beneath churning clouds. The sea rages below.
#
```

### TeleportRoom (Puzzle Outcome)
Checks a clue attribute on the player and teleports them to different locations based on whether the condition is met.

```
@create/drop Puzzle Antechamber;pz_room:evennia.contrib.tutorials.tutorial_world.rooms.TeleportRoom
#
@set Puzzle Antechamber/puzzle_key = clue
@set Puzzle Antechamber/puzzle_value = 2
@set Puzzle Antechamber/success_teleport_to = Treasure Vault
@set Puzzle Antechamber/success_teleport_msg = A hidden door opens silently.
@set Puzzle Antechamber/failure_teleport_to = The Cell
@set Puzzle Antechamber/failure_teleport_msg = The floor crumbles and you fall!
#
```

### Mob AI Setup (Mob)
Spawns an autonomous enemy NPC that patrols and attacks players. Also teleports defeated players.

```
@create/drop Ghost Guardian;ghost:evennia.contrib.tutorials.tutorial_world.mob.Mob
#
@desc Ghost Guardian = An armored phantom floats here, patrolling.
#
@set Ghost Guardian/patrolling = True
@set Ghost Guardian/aggressive = True
@set Ghost Guardian/hunting = True
@set Ghost Guardian/send_defeated_to = The Cell
@set Ghost Guardian/desc_alive = A glowing warrior from another age.
@set Ghost Guardian/desc_dead = A mist lingers where the ghost stood.
@set Ghost Guardian/defeat_msg = You fall as the ghost’s blade strikes!
@set Ghost Guardian/defeat_msg_room = %s crumples under the ghost’s blow.
@set Ghost Guardian/irregular_echoes = ["The ghost moans.", "A chill fills the room."]
@move Ghost Guardian = Castle Entry
#
mobon Ghost Guardian
#
```

### TutorialWeapon + Combat Aliases
Enables use of `slash`, `stab`, and `defend` in combat. Configure weapon stats with `@set`.

```
@create/drop A Rusty Sword;rusty_sword:evennia.contrib.tutorials.tutorial_world.objects.TutorialWeapon
#
@desc A Rusty Sword = A pitted blade, barely functional.
#
@set A Rusty Sword/hit = 0.5
@set A Rusty Sword/damage = 3
@set A Rusty Sword/parry = 0.2
#
```

### Random Weapon Rack (TutorialWeaponRack)
Dispenses one randomized weapon per player from a list. Use for rewards or gear selection.

```
@tel The Armory
#
@create/drop Weapon Barrel;barrel:evennia.contrib.tutorials.tutorial_world.objects.TutorialWeaponRack
#
@desc Weapon Barrel = An open barrel filled with miscellaneous weapons.
#
@set Weapon Barrel/available_weapons = ["longsword", "spear", "dagger"]
@set Weapon Barrel/no_more_weapons_msg = You already took a weapon.
#
```

### Trap Room Using TeleportRoom
Creates a room that automatically teleports the player elsewhere, regardless of state.

```
@create/drop The Trap Room;trap_room:evennia.contrib.tutorials.tutorial_world.rooms.TeleportRoom
#
@set The Trap Room/puzzle_key = flag_that_doesnt_exist
@set The Trap Room/puzzle_value = 1
@set The Trap Room/failure_teleport_to = Dungeon
@set The Trap Room/failure_teleport_msg = A glyph flashes and you vanish!
#

