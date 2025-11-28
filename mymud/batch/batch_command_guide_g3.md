# Evennia Batch-Command Guide (Gen 3 - Simple Adventure Edition)

> **Role:** The Authoritative Reference for AI Builders.
> **Purpose:** To provide the standard for creating complex, interactive MUD zones using Evennia's batch-command processor (`.ev` files).
> **Philosophy:** Strict separation of concerns (Create vs. Link), explicit state management, and rigorous syntax adherence.
> **Implementation:** Uses `typeclasses.simple_adventure` instead of the legacy `tutorial_world` contrib to ensure stability and compatibility with custom game systems.

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

### Advanced Interactive Features (Simple Adventure)
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
*Uses `AdventureReadable`.*

```ev
@create/drop Dusty Tome;gh_tome:typeclasses.simple_adventure.AdventureReadable
#
@desc Dusty Tome = A heavy book bound in dragon hide.
#
@set Dusty Tome/readable_text = "DO NOT READ THE NEXT PAGE."
#
@lock Dusty Tome = get:false()
#
```

### 3.5. Climbable Object & Hidden Exit
*Uses `AdventureClimbable`. Climbing tags the player, allowing them to see/use a locked exit.*

```ev
# 1. Create the Object
@create/drop Ivy Trellis;gh_trellis:typeclasses.simple_adventure.AdventureClimbable
#
@desc Ivy Trellis = Sturdy vines cling to the wall.
#
@set Ivy Trellis/climb_msg = You climb up and spot a hidden window!
#
@lock Ivy Trellis = get:false()
#

# 2. Create the Exit (Phase 4)
# The tag 'climbed_<object_id>' is set automatically.
# However, knowing the ID in batch is hard.
# ALTERNATIVE: Use standard tags if you can set them, or rely on 'tutorial' category tags.
@open window;out = The Secret Balcony
#
# (Tagging logic may require manual builder intervention or simplified checks)
```

### 3.6. Weapon Rack
*Dispenses items. Uses `TutorialWeaponRack` (Mapped to Simple Adventure).*

```ev
@create/drop Rusty Barrel;gh_barrel:typeclasses.simple_adventure.TutorialWeaponRack
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
*Inherits from `AdventureWeatherRoom`. Emits random messages.*

```ev
# --- PHASE 1 ---
@create/drop The Cliffside;gh_cliff:typeclasses.simple_adventure.AdventureWeatherRoom
#
# Configure messages
@tel The Cliffside
#
@set here/weather_msgs = ["Wind howls.", "Rain falls."]
#
```

### 3.8. Dark Room & Light Source
*Room is blind without light. Object provides light.*

```ev
# --- PHASE 1 ---
@create/drop The Deep Pit;gh_pit:typeclasses.simple_adventure.AdventureDarkRoom
#

# --- PHASE 3 (In a different room usually) ---
@create/drop Torch;gh_torch:typeclasses.simple_adventure.AdventureLightSource
#
@desc Torch = A piece of wood soaked in pitch.
#
```

### 3.9. Bridge Room (Fall Risk)
*A room that checks for movement. Inherits from WeatherRoom.*

```ev
# --- PHASE 1 ---
@create/drop The Rope Bridge;gh_bridge:typeclasses.simple_adventure.BridgeRoom
#

# --- PHASE 3 ---
@tel The Rope Bridge
#
@set here/fall_exit = gh_valley_floor
#
@set here/fall_msg = You slip and fall!
#
```

### 3.10. AI Mob (Patrolling)
*An aggressive NPC that moves.*

```ev
# --- PHASE 3 ---
@tel The Great Hall
#
@create/drop Castle Guardian;guardian:typeclasses.simple_adventure.AdventurePatrolMob
#
@sethome guardian = The Great Hall
#
@set guardian/patrolling = True
#
@set guardian/aggressive = True
#
@set guardian/full_health = 20
#
# Turn it on
mobon guardian
#
```

### 3.11. Teleport Puzzle
*Teleports player based on a key item or tag.*

```ev
# --- PHASE 1 ---
@create/drop Trap Room;gh_trap:typeclasses.simple_adventure.AdventureTeleportRoom
#

# --- PHASE 3 ---
@tel Trap Room
#
# Key can be an object name in inventory OR a tag on the player
@set here/puzzle_key = "Golden Key"
#
@set here/target_success = gh_treasure_room
#
@set here/target_failure = gh_dungeon_cell
#
@set here/msg_success = The floor holds steady.
#
@set here/msg_failure = Click. Whoosh. You fall.
#
```

---

## 4. Troubleshooting & Pitfalls

*   **SyntaxError in Batch:** If you see `SyntaxError` pointing to a python file, DO NOT run the batch again until the python file is fixed. Running it on a broken file creates "ghost" objects that must be manually destroyed.
*   **"Typeclass not found":** Ensure you are using `typeclasses.simple_adventure` and NOT `evennia.contrib...`. The contrib code is often incompatible with custom inventory systems.
*   **Object Crashes:** If an object crashes the game/inventory, it likely does not inherit from `TestAdvObject`. Use `AdventureLightSource` instead of standard `LightSource`.
*   **Infinite Loops:** Do not set a Teleport Room's failure target to itself without a delay or condition change.