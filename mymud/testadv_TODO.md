# TestAdv TODO List

## High Priority

* [x] **Implement Wear/Wield/Remove Commands:** Users need commands to move items between inventory and equipment slots (utilizing the EquipmentHandler).
* [x] **Fix Room Item Display:** Items spawned in a room are not appearing in the room description/content list.
* [x] **Fix `look <item>` Traceback:** Looking at specific spawned items (e.g., "mining pick") causes a traceback.

## Low Priority

* [x] Improve the inventory display format (make it more readable/immersive).
* [x] Make worn/wielded items 'look'able (allow default look item display to access equipment handler)
* [ ] Expand `CmdOpen` to work for doors.
* [ ] Refactor `get_obj_stats` to handle empty descriptions gracefully and conditionally hide irrelevant stats (like combat stats for containers).