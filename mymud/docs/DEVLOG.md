# Development Log

## 2025-12-10

### Changes
- **Bug Fixes:**
    - **Room Item Display:** Resolved an issue where spawned items were not visible in the room description.
    - **Look Command Crash:** Fixed a traceback when looking at items (e.g., "mining pick", "crowbar"). The issue was caused by the item's description method (`get_obj_stats`) assuming the looker always had an `equipment` handler. Added a safety check to `testadv/utils.py` to prevent crashes when viewed by non-standard characters (like the superuser).
    - **Loot Spawning Location:** Fixed an issue where `testloot` spawned items in "Null space" (Location: None) instead of the caller's room. Refactored `testadv/loot_tables.py` to pass a dictionary with `{"prototype_parent": key, "location": loc}` to `spawn()`, which resolved the location assignment failure.
    - **Testloot Persistence:** Added `CmdTestLoot` to `CharacterCmdSet` in `commands/default_cmdsets.py` so the command persists across server reloads.
- **Equipment & Interaction:**
    - **Wield/Wear & Remove Commands:** Implemented `CmdWield` (alias: `wear`) and `CmdRemove` (alias: `unequip`, `unwield`) in `commands/mycommands.py`. These integrate directly with the `EquipmentHandler` to move items between backpack and slots.
    - **Robust Equipment Logic:** Patched `testadv/equipment.py` to ensure `move` operations don't delete items if validation fails, and fixed import issues with `get_bare_hands`.
    - **Look Command Polish:** Refactored `CmdLook` to use a safer "hybrid" approach. It now attempts to find equipped items first; if none are found, it delegates to the standard `super().func()`, preserving default functionality (looking at rooms, accounts, etc.).
- **Random Loot System:**
    - **Loot Tables:** Created a master `loot` table in `testadv/random_tables.py` aggregating all gear types.
    - **Flexibility:** Updated `CmdTestLoot` to default to the `loot` table if no argument is provided, simplifying testing.

- **Container System:**
    - **Feature Implementation:** Implemented functional containers (chests/crates) based on `TestAdvContainer`.
    - **Core Logic:** 
        - Created `TestAdvContainer` in `testadv/objects.py` with `is_open` state and `capacity` attributes.
        - Configured `lockfuncs.py` with `is_open()` helper to enforce lock access.
        - Overrode `return_appearance` to rigorously hide container contents when closed.
    - **Commands:** 
        - Implemented `CmdOpen`, `CmdClose`, and `CmdPut` in `commands/mycommands.py`.
        - Refactored `CmdGet` to inherit from `evennia.contrib.game_systems.containers.containers.CmdContainerGet`. This leverages robust, community-standard parsing for `get <obj> from <container>` while maintaining compatibility with our custom equipment handling.
- **Documentation:**
    - **Batch Build Guide (v5 WIP):** Updated `batch/batch_build_guide_v5_wip.md` to include implementation guides for:
        - **Containers:** Chests/Crates using `testadv.objects.TestAdvContainer`.
        - **Sittables:** Chairs/Benches using `typeclasses.sittables.Sittable`.
        - **Consumables:** Potions/Food using `testadv.objects.TestAdvConsumable`.
        - **Echoing Rooms:** Atmospheric rooms using `testadv.rooms.EchoingRoom`.
        - **Random Loot:** Added reference for loot spawning.

## 2025-12-09

### Changes
- **Feature Planning:**
    - Analyzed `builder_feature_reqs.md` and added a dependency roadmap.
    - Identified "Random Loot Tables" as the Phase 1 priority.
- **Documentation:**
    - Created `buildersv2/request_learning/random_loot_tutorial.md` to guide the implementation of the loot system.
- **Equipment & Inventory System:**
    - Implemented `CmdEquip` and `CmdInventory` in `commands/mycommands.py`.
    - These commands utilize the `EquipmentHandler` to display worn items by slot and backpack contents separately.
    - Logic handles slot names (e.g., "Weapon Hand") and calculates slot usage vs. max capacity (Physical + Reason).
- **Look Command Modification:**
    - Overrode `CmdLook` in `commands/mycommands.py`.
    - Enhanced the search scope to include items currently equipped by the character (in `caller.equipment`), allowing users to `look` at items they are wearing but not holding.

### Thinking
- **Inventory UX:** The default Evennia inventory is a flat list. We needed a distinction between "worn" and "carried" to support the Knave-like slot system where inventory management is a core mechanic.
- **Look Scope:** By default, you can often only look at things in the room or inventory. Since equipment moves "off" the standard inventory list into slots (technically stored in the handler), the Look command needed to be explicitly told where to find them so players can examine their own gear.
