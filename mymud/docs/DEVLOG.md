# Development Log

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