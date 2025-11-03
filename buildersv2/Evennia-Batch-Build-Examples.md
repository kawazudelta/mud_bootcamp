# Evennia Batch Build Examples - LLM Prompt Template

This document serves as a few-shot example template for teaching language models how to create Evennia batch build files using **stateless commands only**. Use this as context when asking an LLM to generate batch files for world-building.

---

## Overview

Evennia supports two types of batch processors for offline world building:

1. **Batch Command Processor** (`.ev` files) - Simple, declarative, recommended for LLM generation
2. **Batch Code Processor** (`.py` files) - Advanced, full Python API access

**This document focuses on `.ev` batch-command files using the stateless, three-phase pattern.**

---

## The Three-Phase Pattern (REQUIRED)

**All batch files MUST follow this structure:**

### Phase 1: Create All Rooms
```bash
@create Room Name:evennia.objects.objects.DefaultRoom
@create Another Room:evennia.objects.objects.DefaultRoom
```

### Phase 2: Describe and Configure Rooms
```bash
@desc Room Name = Description text here...

#

@set Room Name/light = dim
@set Room Name/mood = tense

#
```

### Phase 3: Create All Exits
```bash
@open north;n:Room Name = Another Room
@open south;s:Another Room = Room Name

#
```

**Why this pattern?**
- ✅ Completely stateless - no navigation required
- ✅ Easy to debug - each phase is self-contained
- ✅ Clear topology - all connections visible in Phase 3
- ✅ LLM-friendly - no spatial reasoning needed

---

## ⚠️ Commands to AVOID

**Do NOT use these commands in batch files:**
- ❌ `@dig` - Stateful, depends on current location
- ❌ `@tunnel` - Stateful, depends on current location
- ❌ `@tel` for navigation - Can fail and break the build

**Instead, use:**
- ✅ `@create` - For rooms and objects
- ✅ `@open` - For exits
- ✅ `@desc` - For descriptions
- ✅ `@set` - For attributes

---

## ⚠️ Important Requirements

### ExtendedRoom Contrib Required for `@detail` Command

The examples in this document use the `@detail` command to create examinable room features. This command is **NOT available in default Evennia** - it requires the ExtendedRoom contrib.

**To enable ExtendedRoom:**

1. Edit `game/typeclasses/rooms.py`:
```python
from evennia.contrib.grid.extended_room import ExtendedRoom

class Room(ObjectParent, ExtendedRoom):
    pass
```

2. Edit `game/commands/default_cmdsets.py`:
```python
from evennia.contrib.grid import extended_room

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        self.add(extended_room.ExtendedRoomCmdSet)
```

3. Reload the server: `evennia reload`

**Alternative if ExtendedRoom not available:** Remove `@detail` commands from examples or replace with regular objects.

---

## ⚠️ Note About Example Typeclasses

Many examples in this document reference custom typeclasses like `ReadableObject`, `InspectableObject`, `HiddenObject`, and `NPC`. **These are illustrative examples** - they don't exist in base Evennia and are not included in this repository.

**To use these examples:**
1. Either create these custom typeclasses in your `game/typeclasses/` directory
2. Or replace them with base classes: `Object` and `Character`
3. Or use contrib alternatives like `evennia.contrib.tutorials.talking_npc.TalkingNPC`

**Example: Creating a simple ReadableObject**
```python
# In game/typeclasses/objects.py
from typeclasses.objects import Object

class ReadableObject(Object):
    """An object that can be read."""
    def at_object_creation(self):
        self.db.read_text = "There is nothing written here."
```

---

## Batch Command Files (.ev)

**Command to run:** `@batchcommand path.to.file`

### Example 1: Simple Two-Room Build

```bash
#
# Simple Detective Office Build
# Demonstrates basic three-phase pattern
#

# === PHASE 1: CREATE ROOMS ===
@create Detective Office:evennia.objects.objects.DefaultRoom
@create Joe's Diner:evennia.objects.objects.DefaultRoom

#

# === PHASE 2: DESCRIBE ROOMS ===

# Detective Office
@desc Detective Office =
  A cramped office thick with cigarette smoke. Rain streaks the window,
  casting shadows across stacks of case files and a battered desk.

#

@set Detective Office/light = dim
@set Detective Office/smell = cigarette smoke and cheap bourbon
@set Detective Office/ambient_sound = rain pattering on window

#

# Teleport to Detective Office to add details
@tel Detective Office

#

@detail desk;wooden desk =
  A battered oak desk covered in case files and yellowed newspaper clippings.

#

@detail window;rain-streaked window =
  Rain drums against dirty glass. Neon signs flicker in the alley below.

#

@detail filing cabinet;cabinet =
  Dented metal, one drawer slightly ajar. Smells of dust and old paper.

#

# Joe's Diner
@desc Joe's Diner =
  A 24-hour diner with cracked vinyl booths and a counter lined with chrome stools.
  The coffee's terrible, but the jukebox works and the pie's not bad.

#

@set Joe's Diner/light = fluorescent
@set Joe's Diner/smell = coffee and frying bacon
@set Joe's Diner/ambient_sound = jukebox playing swing

#

# Teleport to Joe's Diner to add details
@tel Joe's Diner

#

@detail counter;chrome counter =
  Polished chrome, scarred by coffee rings and cigarette burns.

#

@detail jukebox =
  A Wurlitzer, lights cycling through reds and blues. Currently playing Artie Shaw.

#

@detail booths;vinyl booths =
  Cracked red vinyl, patched with duct tape in places.

#

# === PHASE 3: CREATE EXITS ===

# Connect Detective Office to Joe's Diner
@open door;wooden door;exit:Detective Office = Joe's Diner
@open door;diner door;back:Joe's Diner = Detective Office

#
```

### Example 2: Hub-and-Spoke Map (Town Square)

```bash
#
# Town Square with four connected areas
# Demonstrates hub-and-spoke topology
#

# === PHASE 1: CREATE ALL ROOMS ===
@create Town Square:evennia.objects.objects.DefaultRoom
@create North Gate:evennia.objects.objects.DefaultRoom
@create South Market:evennia.objects.objects.DefaultRoom
@create East Temple:evennia.objects.objects.DefaultRoom
@create West Docks:evennia.objects.objects.DefaultRoom

#

# === PHASE 2: DESCRIBE ROOMS ===

@desc Town Square =
  The bustling heart of the city. Cobblestones worn smooth by centuries of foot traffic.
  Merchants hawk their wares while street performers compete for coin.

#

@set Town Square/light = bright
@set Town Square/ambient_sound = crowd murmur and distant bell tower

#

@desc North Gate =
  Massive iron gates stand open to the road beyond. Guards in city livery
  inspect travelers and their cargo with bored efficiency.

#

@set North Gate/light = daylight
@set North Gate/smell = horses and dust

#

@desc South Market =
  Canvas awnings shade stalls piled with produce, spices, and sundries.
  The air thick with haggling voices and exotic scents.

#

@set South Market/light = dappled
@set South Market/smell = spices and overripe fruit

#

@desc East Temple =
  White marble columns frame bronze doors. Inside, incense curls toward
  vaulted ceilings where saints gaze down in painted judgment.

#

@set East Temple/light = dim and reverent
@set East Temple/smell = incense and beeswax
@set East Temple/ambient_sound = echoing chants

#

@desc West Docks =
  Wooden piers creak under the weight of crates and barrels. Gulls wheel overhead,
  crying their complaints. Salt spray mists the air.

#

@set West Docks/light = hazy
@set West Docks/smell = brine and tar
@set West Docks/ambient_sound = waves and creaking ropes

#

# === PHASE 3: CREATE ALL EXITS ===

# Hub to spokes
@open north;n:Town Square = North Gate
@open south;s:Town Square = South Market
@open east;e:Town Square = East Temple
@open west;w:Town Square = West Docks

#

# Spokes back to hub
@open south;s:North Gate = Town Square
@open north;n:South Market = Town Square
@open west;w:East Temple = Town Square
@open east;e:West Docks = Town Square

#
```

### Example 3: Linear Dungeon Crawl

```bash
#
# Linear dungeon with progressive difficulty
# Demonstrates sequential room connections
#

# === PHASE 1: CREATE ALL ROOMS ===
@create Dungeon Entrance:evennia.objects.objects.DefaultRoom
@create Torch-Lit Corridor:evennia.objects.objects.DefaultRoom
@create Guard Chamber:evennia.objects.objects.DefaultRoom
@create Trapped Hall:evennia.objects.objects.DefaultRoom
@create Boss Chamber:evennia.objects.objects.DefaultRoom

#

# === PHASE 2: DESCRIBE ROOMS ===

@desc Dungeon Entrance =
  Stone steps descend into damp darkness. Moss clings to walls where daylight
  fades to shadow. The air tastes of old earth and older secrets.

#

@set Dungeon Entrance/light = gloaming
@set Dungeon Entrance/temperature = cool

#

@desc Torch-Lit Corridor =
  Guttering torches cast dancing shadows. Water seeps between flagstones,
  pooling in worn depressions. Something skitters in the dark ahead.

#

@set Torch-Lit Corridor/light = flickering
@set Torch-Lit Corridor/smell = smoke and mildew
@set Torch-Lit Corridor/ambient_sound = dripping water

#

@desc Guard Chamber =
  A vaulted room with alcoves where guards once stood watch. Rusted weapons
  lean against walls. Bones lie scattered among rotted bedrolls.

#

@set Guard Chamber/light = dim
@set Guard Chamber/smell = decay
@set Guard Chamber/danger_level = low

#

@desc Trapped Hall =
  Pressure plates are barely visible beneath dust. Slots in the walls suggest
  mechanisms long dormant. The cautious might notice tripwires.

#

@set Trapped Hall/light = very dim
@set Trapped Hall/danger_level = medium
@set Trapped Hall/trap_active = True

#

@desc Boss Chamber =
  A grand hall with pillars carved in forms no sane mason would attempt.
  At the far end, a throne of bones. The air thrums with wrongness.

#

@set Boss Chamber/light = eerie glow
@set Boss Chamber/smell = sulfur
@set Boss Chamber/ambient_sound = low, resonant hum
@set Boss Chamber/danger_level = extreme

#

# === PHASE 3: CREATE ALL EXITS ===

# Sequential connections
@open down;descend;d:Dungeon Entrance = Torch-Lit Corridor
@open up;ascend;u:Torch-Lit Corridor = Dungeon Entrance

#

@open forward;ahead:Torch-Lit Corridor = Guard Chamber
@open back;retreat:Guard Chamber = Torch-Lit Corridor

#

@open north;n:Guard Chamber = Trapped Hall
@open south;s:Trapped Hall = Guard Chamber

#

@open forward;onward:Trapped Hall = Boss Chamber
@open back;flee:Boss Chamber = Trapped Hall

#
```

### Example 4: Objects and Items

```bash
#
# Creating objects and placing them in rooms
# Demonstrates object creation and placement
#

# === PHASE 1: CREATE ROOMS ===
@create Hidden Library:evennia.objects.objects.DefaultRoom

#

# === PHASE 2: DESCRIBE ROOM ===
@desc Hidden Library =
  Dust motes swirl in shafts of light from high windows. Floor-to-ceiling shelves
  groan under the weight of forgotten tomes. The smell of old leather and secrets.

#

@set Hidden Library/light = dusty shafts
@set Hidden Library/smell = old books and leather
@set Hidden Library/ambient_sound = profound silence

#

# === CREATE OBJECTS ===

# Readable letter
@create sealed letter;letter;envelope:typeclasses.objects.ReadableObject

#

@desc sealed letter =
  An envelope of cream vellum, sealed with red wax bearing an unfamiliar crest.

#

@set sealed letter/read_text =
  "The bearer of this letter is charged with discovering the truth about
  the incident at Ravencrest Manor. Trust no one. Burn this after reading.
  - M."

#

@tel sealed letter = Hidden Library

#

# Ancient tome
@create ancient tome;tome;book:typeclasses.objects.ReadableObject

#

@desc ancient tome =
  A leather-bound volume, its pages yellowed and brittle. The title is in a language
  you don't recognize, but the diagrams are disturbingly clear.

#

@set ancient tome/read_text =
  The text is incomprehensible, but the illustrations depict rituals you wish
  you could unsee. One page seems to be a map - or a summoning circle.

#

@set ancient tome/cursed = True
@set ancient tome/quest_item = True

#

@tel ancient tome = Hidden Library

#

# Rusty key
@create rusty key;key:typeclasses.objects.QuestItem

#

@desc rusty key =
  A heavy iron key, mottled with rust. It looks old - very old. What door
  has waited centuries for this key to turn?

#

@set rusty key/opens = "ancient_vault_door"
@set rusty key/quest_id = "manor_mystery"

#

@tel rusty key = Hidden Library

#
```

### Example 5: Complex Room with ExtendedRoom Details

```bash
#
# Detailed noir detective office with extensive use of @detail
# Demonstrates atmospheric world-building
#

# === PHASE 1: CREATE ROOM ===
@create Spade's Office:evennia.contrib.grid.extended_room.ExtendedRoom

#

# === PHASE 2: DESCRIBE AND DETAIL ===

@desc Spade's Office =
  The office of a man who's seen better days and worse cases. A desk anchors
  the room like a ship in a sea of cigarette butts and broken dreams. Rain
  streaks the window. The venetian blinds paint shadows across everything.

#

@set Spade's Office/light = noir
@set Spade's Office/smell = cigarettes and bourbon
@set Spade's Office/ambient_sound = rain on window, distant traffic
@set Spade's Office/temperature = cool
@set Spade's Office/mood = melancholy

#

# Teleport to room to add details
@tel Spade's Office

#

@detail desk;oak desk =
  A scarred oak battleship that's fought a thousand losing battles with paperwork.
  Cigarette burns crater the edge. A bottle of cheap bourbon in the drawer - less
  than you'd like, more than you should.

#

@detail window;rain-streaked window;blinds;venetian blinds =
  Rain drums against the glass. Through the slats of the venetian blinds, neon
  signs flicker in the alley below. Red. Green. Red again. Someone's watching from
  the shadows - or are they?

#

@detail filing cabinet;cabinet =
  Four drawers of dented green metal. The lock on the bottom drawer is broken.
  Inside: case files, a .38 revolver, and a photograph you try not to look at.

#

@detail photograph;photo;picture =
  Her. Before everything went wrong. Before the case you couldn't solve and the
  questions that won't let you sleep. You should throw it away. You won't.

#

@detail ashtray;cigarette butts =
  An overflowing ashtray on the desk, still smoldering. Lucky Strikes. You've been
  here all night again. The case isn't getting any warmer, but the trail of smoke
  is fresh.

#

@detail bottle;bourbon;whiskey =
  Cheap bourbon. The kind that burns going down and makes you feel worse after.
  The label promises "smooth," which is the first lie you've heard today but won't
  be the last.

#

@detail telephone;phone;rotary phone =
  A black rotary phone, waiting to ring with news you don't want. The cord's tangled
  like your thoughts. Last call was from her - or someone claiming to be her. The
  dame's dead. You saw the body. Didn't you?

#

@detail shadows;shadow patterns =
  The blinds throw prison bar shadows across everything. Appropriate, really.
  This office is a cell you built yourself, sentence unknown, parole denied.

#

@detail neon signs;neon;alley =
  Through the window: a burlesque club, a pawn shop, a fortune teller who couldn't
  predict her own arrest. The neon flickers like dying fireflies, each one a small
  broken promise.

#
```

### Example 6: Multi-Area Build (Noir City District)

```bash
#
# Complete city district with multiple connected locations
# Demonstrates large-scale batch building
#

# === PHASE 1: CREATE ALL ROOMS ===

# Main street
@create Rain-Slicked Street:evennia.contrib.grid.extended_room.ExtendedRoom
@create Dark Alley:evennia.contrib.grid.extended_room.ExtendedRoom

#

# Buildings
@create Joe's Diner:evennia.contrib.grid.extended_room.ExtendedRoom
@create Spade Detective Agency:evennia.contrib.grid.extended_room.ExtendedRoom
@create Blue Moon Bar:evennia.contrib.grid.extended_room.ExtendedRoom
@create Pawn Shop:evennia.contrib.grid.extended_room.ExtendedRoom

#

# === PHASE 2: DESCRIBE ALL ROOMS ===

# Rain-Slicked Street
@desc Rain-Slicked Street =
  The street gleams with rain and broken neon promises. Water streams along
  the gutter carrying cigarette butts and yesterday's racing forms. Somewhere
  a saxophone plays, lonely as the night is long.

#

@set Rain-Slicked Street/light = neon-tinged darkness
@set Rain-Slicked Street/smell = rain and asphalt
@set Rain-Slicked Street/ambient_sound = rain, distant traffic, saxophone

#

# Dark Alley
@desc Dark Alley =
  The kind of alley where deals go bad and bodies go cold. Fire escapes
  zigzag up brick walls. Trash cans overflow with secrets nobody wants.
  A cat watches you with knowing eyes.

#

@set Dark Alley/light = very dark
@set Dark Alley/smell = garbage and danger
@set Dark Alley/danger_level = medium

#

# Joe's Diner
@desc Joe's Diner =
  Chrome and vinyl, coffee and grease. The jukebox plays swing standards
  to an audience of insomniacs and bad decisions. Joe doesn't ask questions,
  which is why you come here.

#

@set Joe's Diner/light = harsh fluorescent
@set Joe's Diner/smell = coffee and bacon grease
@set Joe's Diner/ambient_sound = jukebox and sizzling grill

#

# Spade Detective Agency
@desc Spade Detective Agency =
  Three flights up, fourth door on the left. The paint on the door says
  "Spade Detective Agency - Discreet Inquiries." The paint's peeling.
  So's your faith in humanity.

#

@set Spade Detective Agency/light = dim
@set Spade Detective Agency/smell = cigarettes and old coffee

#

# Blue Moon Bar
@desc Blue Moon Bar =
  Smoke hangs heavy as regret. The piano player knows three songs and the
  bartender knows when to be deaf. The kind of place where you drink to
  forget and remember why you started drinking.

#

@set Blue Moon Bar/light = blue-tinged gloom
@set Blue Moon Bar/smell = cigarettes and spilled gin
@set Blue Moon Bar/ambient_sound = piano and low conversation

#

# Pawn Shop
@desc Pawn Shop =
  Barred windows frame a display of broken dreams: wedding rings, watches,
  a saxophone that'll never play the Blue Room again. Everything has a price.
  Most things cost more than they're worth.

#

@set Pawn Shop/light = yellow and suspicious
@set Pawn Shop/smell = dust and desperation

#

# === PHASE 3: CREATE ALL EXITS ===

# Street to alley
@open alley;dark alley;into alley:Rain-Slicked Street = Dark Alley
@open street;out;back to street:Dark Alley = Rain-Slicked Street

#

# Street to buildings
@open door;diner door:Rain-Slicked Street = Joe's Diner
@open door;out;exit:Joe's Diner = Rain-Slicked Street

#

@open stairs;stairwell;up:Rain-Slicked Street = Spade Detective Agency
@open stairs;down;street:Spade Detective Agency = Rain-Slicked Street

#

@open blue door;bar door:Rain-Slicked Street = Blue Moon Bar
@open door;out:Blue Moon Bar = Rain-Slicked Street

#

# Alley connections
@open pawn shop door;door:Dark Alley = Pawn Shop
@open alley door;back alley;out:Pawn Shop = Dark Alley

#
```

---

## Best Practices Summary

### DO:
✅ Use the three-phase pattern (Create → Describe → Connect)
✅ Use stateless commands (@create, @open, @desc, @set)
✅ Use explicit room names (never "here")
✅ Terminate multi-line commands with `#`
✅ Add blank lines between command groups for readability
✅ Include comments explaining sections
✅ Test incrementally with small builds first

### DON'T:
❌ Use @dig or @tunnel (stateful, location-dependent)
❌ Use @tel for navigation (can fail, breaks build)
❌ Use `@desc here` (unreliable in batch files)
❌ Create exit direction conflicts
❌ Forget `#` terminators on multi-line commands
❌ Mix phases (create all rooms first, then describe, then connect)

---

## Template for LLM Generation

When asking an LLM to generate a batch file, provide this template:

```
Generate an Evennia batch-command file (.ev) for [DESCRIPTION].

Requirements:
- Use ONLY stateless commands: @create, @open, @desc, @set
- Follow the three-phase pattern strictly:
  Phase 1: Create all rooms with @create
  Phase 2: Describe rooms with @desc and @set
  Phase 3: Create exits with @open
- Do NOT use @dig, @tunnel, or @tel for navigation
- Use explicit room names, never "here"
- Terminate multi-line commands with #
- Add blank # lines between command groups

Room requirements:
- [NUMBER] rooms total
- [DESCRIPTION OF TOPOLOGY]
- Atmospheric descriptions with sensory details
- Custom attributes: light, smell, ambient_sound, mood

Example structure:
# === PHASE 1: CREATE ROOMS ===
@create Room Name:evennia.objects.objects.DefaultRoom
...

# === PHASE 2: DESCRIBE ROOMS ===
@desc Room Name = Description...
#
@set Room Name/light = value
...

# === PHASE 3: CREATE EXITS ===
@open direction;aliases:Source Room = Destination Room
...
```

---

## Common Patterns Quick Reference

### Creating a Room
```bash
@create Room Name:evennia.objects.objects.DefaultRoom
```

### Describing a Room
```bash
@desc Room Name =
  Multi-line description here.
  Can span multiple lines.

#
```

### Setting Attributes
```bash
@set Room Name/attribute = value
```

### Creating Bidirectional Exit
```bash
@open north;n:Room A = Room B
@open south;s:Room B = Room A
```

### Creating Custom Exit
```bash
@open wooden door;door;entrance:Room A = Room B
@open hallway;hall;back:Room B = Room A
```

### Creating and Placing Object
```bash
@create object name:typeclass
@desc object name = Description...
#
@tel object name = Room Name
```

---

**End of Examples Document**

For technical reference and detailed command documentation, see: `Evennia-Batch-Build-Technical-Reference.md`
