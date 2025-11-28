# Evennia Batch-Command Guide (Gen 4 - Core Features Only)

> **Role:** The Authoritative Reference for AI Builders.
> **Purpose:** To provide the standard for creating complex, interactive MUD zones using Evennia's batch-command processor (`.ev` files).
> **Philosophy:** Strict separation of concerns (Create vs. Link), explicit state management, and rigorous syntax adherence.
> **Scope:** Limited to verified, core features supported by the base Evennia installation and the `TestAdv` system. **Do not use `contrib.tutorial_world` or experimental features.**

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
- [x] **Rooms & Descriptions:** Standard room creation (`typeclasses.rooms.Room`).
- [x] **Two-Way Exits:** Explicit linking between rooms (`typeclasses.exits.Exit`).
- [x] **Static Props:** Scenery objects (tables, statues) that cannot be picked up (`typeclasses.objects.Object` with `@lock get:false()`).
- [x] **Inventory Items:** Lootable objects compatible with `TestAdv` (`testadv.objects.TestAdvObject`).

### Advanced Features (Reserved)
*These features require custom Python development and are NOT currently available via standard batch commands.*
- [ ] Room Details (Non-object look targets)
- [ ] Readable Objects
- [ ] Climbable Objects
- [ ] Weapon Racks
- [ ] Dark Rooms
- [ ] Light Sources
- [ ] Weather Rooms
- [ ] Bridge Rooms
- [ ] Teleport Puzzles
- [ ] Active Mobs

---

## 3. Implementation Cookbook

### 3.1. Basic Room & Exit
*Use standard `typeclasses.rooms.Room`.*

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

### 3.3. Lootable Items (TestAdv Compatible)
*Use `testadv.objects.TestAdvObject` or specific subclasses like `testadv.objects.TestAdvWeapon`.*

```ev
# --- PHASE 3 ---
@tel The Armory
#
@create/drop Rusty Sword;sword_01:testadv.objects.TestAdvWeapon
#
@desc Rusty Sword = A pitted iron blade.
#
# Optional: Set properties manually if needed, though defaults are usually fine.
# @set Rusty Sword/damage_roll = "1d6"
```

---

## 4. Troubleshooting

*   **Commands merging?** You forgot the `#` separator line.
*   **"Object not found" errors?** You are likely trying to Describe or Decorate a room you haven't `@create`d yet (check Phase order), or you are trying to decorate a room you haven't `@tel`eported to.
*   **Descriptions not sticking?** Ensure you are targeting the object by its Alias or Name correctly.
*   **Item Crashing Inventory?** Ensure you created it using `testadv.objects.TestAdvObject` (or subclass), NOT `typeclasses.objects.Object`. The custom inventory system requires the `TestAdv` parent.