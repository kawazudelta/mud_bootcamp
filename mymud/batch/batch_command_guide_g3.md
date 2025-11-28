# Evennia Batch-Command Guide (Gen 3)

> **Role:** The Authoritative Reference for AI Builders.
> **Purpose:** To provide the standard for creating complex, interactive MUD zones using Evennia's batch-command processor (`.ev` files).
> **Philosophy:** Strict separation of concerns (Create vs. Link), explicit state management, and rigorous syntax adherence.

---

## 1. The Golden Rules

### 1.1. The Separator Rule
**Every command line must be followed by a blank comment line (`#`).**
Evennia's batch processor merges lines that are not separated. Failing to include this separator is the #1 cause of build errors.

*   ❌ **Wrong:**
    ```ev
    @create/drop Box
    @desc Box = It is a box.
    ```
    *(Result: Evennia tries to execute `@create/drop Box @desc Box...` as one command)*

*   ✅ **Right:**
    ```ev
    @create/drop Box:objects.Object
    #
    @desc Box = It is a box.
    #
    ```

### 1.2. The Four-Phase Build Pattern
To prevent "drift" (where the builder is in the wrong room for a command), we strictly separate the build into four phases.

1.  **Phase 1: Create Rooms (Stateless)**
    *   Create all room objects.
    *   Use `@create/drop`.
    *   Do not describe, decorate, or link yet.
2.  **Phase 2: Describe Rooms (Stateless)**
    *   Apply descriptions to the rooms created in Phase 1.
    *   Use `@desc`.
3.  **Phase 3: Decorate Rooms (Stateful)**
    *   `@tel` to a room.
    *   Create objects, mobs, and details *inside* that room.
    *   Lock them (`get:false()`).
4.  **Phase 4: Link Rooms (Stateful)**
    *   `@tel` to a room.
    *   Create exits *out* of that room using `@open`.

### 1.3. Naming Convention
**Display Name First; Alias Second.**
*   **Format:** `@create/drop Display Name;alias_slug:typeclass`
*   **Rooms:** Title Case (e.g., "The Obsidian Hall").
*   **Objects:** Singular, no article (e.g., "Iron Torch"). Evennia adds "a/an" automatically.
*   **Aliases:** Snake_case, unique to zone (e.g., `la_obsidian_hall`, `la_torch`).

---

## 2. Capability Checklist

This guide supports the implementation of the following features. Use this checklist to validate AI-generated content.

### Core Structure
- [x] **Rooms & Descriptions:** Standard room creation.
- [x] **Two-Way Exits:** explicit linking between rooms.
- [x] **Static Props:** Scenery objects (tables, statues) that cannot be picked up.
- [x] **Room Details:** Non-object look targets (`@detail`).

### Advanced Interactive Features (Tutorial World)
- [x] **Readable Objects:** Signs or books with text.
- [x] **Climbable Objects:** Reveal hidden exits/info when climbed.
- [x] **Weapon Racks:** Dispense unique items to players.
- [x] **Dark Rooms:** Require a light source to see descriptions.
- [x] **Light Sources:** Burnable items that illuminate Dark Rooms.
- [x] **Weather Rooms:** Emit random atmospheric messages.
- [x] **Bridge Rooms:** Simulate dangerous crossings / fall risks.
- [x] **Teleport Puzzles:** Rooms that divert travel based on player tags/clues.
- [x] **Active Mobs:** Patrolling, aggressive NPCs.

---

## 3. Implementation Cookbook

### 3.1. Basic Room & Exit
*Note: Use standard `typeclasses.rooms.Room` unless a special feature is needed.*

```ev
# --- PHASE 1 ---
@create/drop The Great Hall;gh_hall:typeclasses.rooms.Room
#
@create/drop The Garden;gh_garden:typeclasses.rooms.Room
#

# --- PHASE 2 ---
@desc The Great Hall = A vast hall of stone.
#
@desc The Garden = Green and vibrant.
#

# --- PHASE 4 ---
@tel The Great Hall
#
@open north;n = The Garden
#
@tel The Garden
#
@open south;s = The Great Hall
#
```

### 3.2. Static Props (Scenery)
*Props add flavor. Always lock them so players don't steal the furniture.*

```ev
# --- PHASE 3 ---
@tel The Great Hall
#
@create/drop Grand Chandelier;gh_chandelier;light:typeclasses.objects.Object
#
@desc Grand Chandelier = Thousands of crystals catch the light.
#
@lock Grand Chandelier = get:false()
#
```

### 3.3. Room Details (`@detail`)
*Adds "virtual" objects to a room description without creating database objects.*

```ev
# --- PHASE 3 ---
@tel The Great Hall
#
@detail floor;stones = The stones are worn smooth by centuries of footsteps.
#
```

### 3.4. Readable Object
*Uses `TutorialReadable`.*

```ev
@create/drop Dusty Tome;gh_tome:evennia.contrib.tutorials.tutorial_world.objects.TutorialReadable
#
@desc Dusty Tome = A heavy book bound in dragon hide.
#
@set Dusty Tome/readable_text = "DO NOT READ THE NEXT PAGE."
#
@lock Dusty Tome = get:false()
#
```

### 3.5. Climbable Object & Hidden Exit
*Uses `TutorialClimbable`. Climbing tags the player, allowing them to see/use a locked exit.*

```ev
# 1. Create the Object
@create/drop Ivy Trellis;gh_trellis:evennia.contrib.tutorials.tutorial_world.objects.TutorialClimbable
#
@desc Ivy Trellis = Sturdy vines cling to the wall.
#
@set Ivy Trellis/climb_text = You climb up and spot a hidden window!
#
@lock Ivy Trellis = get:false()
#

# 2. Create the Exit (Phase 4)
# The tag 'tutorial_climbed_tree' is hardcoded in the TutorialClimbable class (default).
@open window;out = The Secret Balcony
#
@lock window = view:tag(tutorial_climbed_tree, tutorial_world);traverse:tag(tutorial_climbed_tree, tutorial_world)
#
```

### 3.6. Weapon Rack
*Dispenses items. Uses `TutorialWeaponRack`.*

```ev
@create/drop Rusty Barrel;gh_barrel:evennia.contrib.tutorials.tutorial_world.objects.TutorialWeaponRack
#
@desc Rusty Barrel = Full of old swords.
#
@set Rusty Barrel/rack_id = "hall_barrel_1"
#
@set Rusty Barrel/available_weapons = ["dagger", "sword", "club"]
#
@set Rusty Barrel/no_more_weapons_msg = You already took one!
#
@lock Rusty Barrel = get:false()
#
```

### 3.7. Weather Room
*Inherits from `WeatherRoom`. Emits random messages.*

```ev
# --- PHASE 1 ---
@create/drop The Cliffside;gh_cliff:evennia.contrib.tutorials.tutorial_world.rooms.WeatherRoom
#
# (No extra config needed, just standard description)
```

### 3.8. Dark Room & Light Source
*Room is blind without light. Object provides light.*

```ev
# --- PHASE 1 ---
@create/drop The Deep Pit;gh_pit:evennia.contrib.tutorials.tutorial_world.rooms.DarkRoom
#

# --- PHASE 3 (In a different room usually) ---
@create/drop Torch;gh_torch:evennia.contrib.tutorials.tutorial_world.objects.LightSource
#
@desc Torch = A piece of wood soaked in pitch.
#
```

### 3.9. Bridge Room (Fall Risk)
*A room that takes time to cross. Logic is in the attributes.*

```ev
# --- PHASE 1 ---
@create/drop The Rope Bridge;gh_bridge:evennia.contrib.tutorials.tutorial_world.rooms.BridgeRoom
#

# --- PHASE 3 ---
@tel The Rope Bridge
#
@set here/west_exit = gh_cliff_edge
#
@set here/east_exit = gh_castle_gate
#
@set here/fall_exit = gh_valley_floor
#
```

### 3.10. AI Mob (Patrolling)
*An aggressive NPC that moves.*

```ev
# --- PHASE 3 ---
@tel The Great Hall
#
@create/drop Castle Guardian;guardian:evennia.contrib.tutorials.tutorial_world.mob.Mob
#
@sethome guardian = The Great Hall
#
@set guardian/patrolling = True
#
@set guardian/aggressive = True
#
@set guardian/hunting = True
#
@set guardian/desc_alive = A towering suit of animated armor.
#
@set guardian/desc_dead = A pile of scrap metal.
#
# Equip the mob (create weapon -> teleport to mob)
@create/drop Giant Sword;mob_sword:evennia.contrib.tutorials.tutorial_world.objects.TutorialWeapon
#
@tel/quiet mob_sword = guardian
#
# Turn it on
mobon guardian
#
```

### 3.11. Teleport Puzzle (The "Tomb")
*Teleports player based on a puzzle state (usually a tag).*

```ev
# --- PHASE 1 ---
@create/drop Trap Room;gh_trap:evennia.contrib.tutorials.tutorial_world.rooms.TeleportRoom
#

# --- PHASE 3 ---
@tel Trap Room
#
# 0 = correct puzzle value
@set here/puzzle_value = 0
#
@set here/success_teleport_to = gh_treasure_room
#
@set here/failure_teleport_to = gh_dungeon_cell
#
@set here/success_teleport_msg = The floor holds steady.
#
@set here/failure_teleport_msg = Click. Whoosh. You fall.
#
```

---

## 4. Troubleshooting

*   **Commands merging?** You forgot the `#` separator line.
*   **"Object not found" errors?** You are likely trying to Describe or Decorate a room you haven't `@create`d yet (check Phase order), or you are trying to decorate a room you haven't `@tel`eported to.
*   **Descriptions not sticking?** Ensure you are targeting the object by its Alias or Name correctly.
*   **Mobs not moving?** Did you run `mobon <mob>`?
