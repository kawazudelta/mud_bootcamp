# Evennia Batch Build Technical Reference

**Companion Document to:** `Evennia-Batch-Build-Examples.md`

This document explains the technical concepts, commands, and Evennia-specific terminology used in batch building. Use this alongside the examples document to understand the **how** and **why** of batch file creation.

---

## Table of Contents

1. [Batch File Philosophy: Stateless Creation](#batch-file-philosophy-stateless-creation)
2. [Core Evennia Concepts](#core-evennia-concepts)
3. [Batch Building Commands (Stateless)](#batch-building-commands-stateless)
4. [Typeclasses Explained](#typeclasses-explained)
5. [Attributes System](#attributes-system)
6. [Object Hierarchy & Properties](#object-hierarchy--properties)
7. [Exits and Room Connectivity](#exits-and-room-connectivity)
8. [Locks and Permissions](#locks-and-permissions)
9. [Python API for Batch Code](#python-api-for-batch-code)
10. [Common Patterns Explained](#common-patterns-explained)
11. [Troubleshooting & Best Practices](#troubleshooting--best-practices)
12. [Interactive Building Commands (Not for Batch Files)](#interactive-building-commands-not-for-batch-files)

---

## Batch File Philosophy: Stateless Creation

### The Problem with Stateful Building

Traditional MUD building commands like `@dig` and `@tunnel` were designed for **interactive, human builders** who walk around the game world creating rooms as they go. These commands are **stateful** - they depend on your current location and move you around as side effects.

**Why this is bad for batch files:**
- 🔴 **Navigation can fail** - If `@tel` fails, the entire build breaks
- 🔴 **Hard to debug** - Need to trace where you are at each step
- 🔴 **Fragile topology** - Rooms get connected to wrong places when navigation breaks
- 🔴 **Order-dependent** - Commands must execute in exact sequence
- 🔴 **Confusing for LLMs** - Mixes spatial navigation with object creation

### The Stateless Solution

**For batch file generation, use stateless commands exclusively:**

| Command | What It Does | Depends on Location? |
|---------|-------------|---------------------|
| `@create` | Create rooms/objects | ❌ No |
| `@open` | Create exits between named rooms | ❌ No |
| `@desc` | Set descriptions on named objects | ❌ No |
| `@set` | Set attributes on named objects | ❌ No |
| `@detail` | Add details to named rooms | ⚠️ Yes (see note) |

⚠️ **Note on @detail:** While `@detail` operates on your current room (stateful), we can use it safely in Phase 2 after creating rooms with `@create`. This is acceptable because we're not relying on navigation.

### The Three-Phase Pattern

**Phase 1: Create all rooms (no exits)**
```bash
@create Forest Edge:evennia.objects.objects.DefaultRoom
@create Moonlit Glade:evennia.objects.objects.DefaultRoom
@create Dark Cave:evennia.objects.objects.DefaultRoom
```

**Phase 2: Add descriptions and attributes**
```bash
@desc Forest Edge = The trees marshal themselves like sentries...
@set Forest Edge/light = gloaming
@detail hedge = A wild hedge hints at riot.
```

**Phase 3: Create all exits with explicit source/destination**
```bash
@open in;into wood:Forest Edge = Moonlit Glade
@open out;back:Moonlit Glade = Forest Edge
@open north;n:Moonlit Glade = Dark Cave
@open south;s:Dark Cave = Moonlit Glade
```

### Benefits of Stateless Building

✅ **Completely declarative** - Commands work regardless of your location
✅ **Easy to debug** - Each command is self-contained
✅ **Clear topology** - You can see exactly what connects where
✅ **Parallel-safe** - Commands can theoretically run in any order (within phases)
✅ **LLM-friendly** - No spatial reasoning required, just structured data
✅ **Modifiable** - Want to add an exit? Just add one line anywhere in Phase 3

### Commands to AVOID in Batch Files

| Command | Why Avoid | Use Instead |
|---------|-----------|-------------|
| `@dig` | Stateful - moves you, creates exits implicitly | `@create` + `@open` |
| `@tunnel` | Stateful - moves you, limited to compass directions | `@create` + `@open` |
| `@tel` | Stateful - navigation can fail in batch context | Not needed |

These commands are documented at the end of this file for reference, but **should not be used in LLM-generated batch files**.

---

## Core Evennia Concepts

### The Object Model

Everything in an Evennia game is an **Object** - characters, rooms, items, exits, NPCs. The Object is the fundamental building block.

**Key Principle:** All game entities inherit from `DefaultObject` and share common functionality.

**Object Types:**
- **Object** - Base class for things (items, furniture, props)
- **Character** - Puppetable entities (PCs, NPCs)
- **Room** - Locations in the game world
- **Exit** - One-way connections between rooms

```
┌─────────────┐
│DefaultObject│  ← Base class provided by Evennia
└──────┬──────┘
       │
   ┌───┴────┬──────┬────────┐
   │        │      │        │
 Object  Character Room   Exit
```

### Database IDs (dbrefs)

Every object in Evennia gets a unique database reference number called a **dbref**. You'll see these as `#2`, `#15`, `#143`, etc.

**Why this matters:**
- Database IDs are permanent and never change
- Use dbrefs to reference specific objects in batch files
- `#2` is typically Limbo (the default starting room)

**Finding dbrefs:**
```bash
# In-game
look
# Shows: Limbo(#2)

@examine object
# Shows detailed info including dbref
```

### The Key/Alias System

**Key** - The primary name of an object
**Aliases** - Alternative names for the same object

```bash
# Creating an object with aliases
@create envelope;letter;note
# Key: "envelope"
# Aliases: "letter", "note"
```

Players can use any of these names to reference the object:
- `get envelope` ✓
- `get letter` ✓
- `get note` ✓

---

## Batch Building Commands (Stateless)

These are the **primary commands for batch file generation**. They are stateless and work regardless of your current location.

### @create - Creating Objects and Rooms

**Syntax:**
```bash
@create <name>[;aliases][:typeclass]
```

**What it does:**
Creates an object or room. For rooms, specify the Room typeclass explicitly.

**Examples:**
```bash
# Create a room
@create Detective Office:evennia.objects.objects.DefaultRoom

# Room with aliases
@create Dark Alley;alley;backstreet:evennia.objects.objects.DefaultRoom

# Room with custom typeclass
@create Mystic Chamber;chamber:typeclasses.rooms.MagicRoom

# Create a simple object (goes in inventory)
@create letter

# Object with aliases
@create sealed envelope;envelope;letter

# Object with custom typeclass
@create magical sword:typeclasses.objects.MagicalWeapon

# Object with both aliases and typeclass
@create ornate key;key;skeleton key:typeclasses.objects.QuestItem
```

**Typeclass paths:**
- **Default Room:** `evennia.objects.objects.DefaultRoom` (use this for standard rooms)
- **Custom Room:** `typeclasses.rooms.YourRoomClass`
- **Default Object:** (omit typeclass, uses default)
- **Custom Object:** `typeclasses.objects.YourObjectClass`

**Important:**
- Rooms are objects too! Specify `:evennia.objects.objects.DefaultRoom` to create a room
- Without a typeclass, `@create` makes a regular object (item)
- Objects are created in your inventory by default

### @open - Creating Exits Between Rooms

**Syntax:**
```bash
@open <exit name>[;aliases][:<typeclass>] [= <destination>]
```

**Enhanced syntax for batch files:**
```bash
@open <exit name>[;aliases]:<source room> = <destination room>
```

**What it does:**
Creates a one-way Exit connecting two rooms. The exit is created from the source room to the destination room.

**Examples:**
```bash
# Basic exit from current room to a destination
@open door = Detective Office

# Exit with aliases
@open wooden door;door;entrance = Detective Office

# Explicit source and destination (best for batch files)
@open north;n:Moonlit Glade = Dark Cave

# Exit with custom typeclass
@open secret passage:typeclasses.exits.HiddenExit = Hidden Chamber

# Create bidirectional connection (two commands)
@open north;n:Room A = Room B
@open south;s:Room B = Room A
```

**Batch File Pattern:**
```bash
# Phase 1: Create rooms
@create Room A:evennia.objects.objects.DefaultRoom
@create Room B:evennia.objects.objects.DefaultRoom

#

# Phase 3: Create exits
@open north;n:Room A = Room B
@open south;s:Room B = Room A
```

**Important Notes:**
- One `@open` command creates ONE exit (one-way)
- For bidirectional travel, create two exits (one in each direction)
- Always use room names, not "here" in batch files
- The `:source room` syntax lets you create exits from any room, regardless of your location

### @desc - Setting Descriptions

**Syntax:**
```bash
@desc <object name> = <description text>
```

**What it does:**
Sets the description (what players see when they `look at` something).

**Examples:**
```bash
# Describe a room (use explicit name, not "here")
@desc Detective Office =
  A cramped office thick with cigarette smoke. Rain streaks the window,
  casting shadows across stacks of case files and a battered desk.

#

# Describe an object
@desc letter = A sealed envelope with a red wax seal.

#

# Multi-paragraph descriptions (two blank lines = paragraph break)
@desc Moonlit Glade =
  A bowl of grass whose rim is trees; the moon, being curious, lingers here.
  The turf remembers dances that no license granted.


  Desire finds echo in this clearing, and echo, being mischievous,
  frequently answers the wrong caller.

#
```

**Batch file rules:**
- ❌ **Never use `@desc here`** - doesn't work reliably in batch files
- ✅ **Always use explicit object/room names**
- ✅ **Terminate multi-line descriptions with `#`** (comment terminator)

**Technical note:**
This sets the `db.desc` Attribute on the object. The `look` command reads this Attribute to show descriptions.

### @set - Setting Attributes

**Syntax:**
```bash
@set <object name>/<attribute name> = <value>
```

**What it does:**
Sets an Attribute (persistent data) on an object. Attributes survive server reboots.

**Examples:**
```bash
# String attributes
@set Detective Office/mood = noir
@set Detective Office/time_of_day = night

#

# Number attributes
@set sword/damage = 10
@set sword/durability = 100.5

#

# Boolean attributes
@set sword/magical = True
@set sword/cursed = False

#

# List attributes
@set sword/damage_types = ["slashing", "piercing"]

#

# Dict attributes
@set sword/stats = {"str": 5, "dex": 2}

#

# Tuple attributes
@set sword/rgb_color = (255, 100, 50)

#
```

**Common Custom Attributes:**
```bash
# Atmospheric attributes (custom to your game)
@set Room/light = gloaming
@set Room/smell = cigarette smoke and cheap bourbon
@set Room/ambient_sound = rain pattering on window
@set Room/temperature = cold
@set Room/mood = tense

#

# Object attributes
@set Object/value = 100
@set Object/weight = 5.5
@set Object/material = steel
@set Object/condition = worn

#
```

**Special Built-in Attributes:**
```bash
# desc - What players see with 'look'
@set obj/desc = Description text

#

# get_text - Message when picked up
@set obj/get_text = You pick up the key.

#

# drop_text - Message when dropped
@set obj/drop_text = The key clatters to the ground.

#
```

**View attributes:**
```bash
# View single attribute
@set obj/attribute_name

# View all attributes
@examine obj
```

### @detail - Adding Examinable Details

⚠️ **Requires ExtendedRoom Contrib** - This command is NOT available in default Evennia.

**Syntax:**
```bash
@detail[/del] <detail name>[;aliases] = <description>
```

**What it does:**
Adds named details to a room that players can examine without creating separate objects.

⚠️ **Important Limitation:** `@detail` operates on your CURRENT room only. In batch files, you must navigate to the room first using `@tel`, or create the room with `@create` and then immediately add details before moving.

**Examples:**
```bash
# Basic detail
@detail window = A grimy window looking out onto the street.

#

# Multiple aliases for same detail
@detail desk;wooden desk;oak desk = An old desk covered in papers.

#

# Remove a detail
@detail/del window

#
```

**Batch File Pattern:**
```bash
# Create room
@create Detective Office:evennia.objects.objects.DefaultRoom

#

# Teleport to it
@tel Detective Office

#

# Add details while you're there
@detail window = A grimy window streaked with rain.

#

@detail desk;wooden desk = A battered oak desk covered in case files.

#

@detail ashtray = An overflowing ashtray, still smoldering.

#
```

**Why use details?**
- ✅ No database overhead (stored as Attribute on room)
- ✅ Players can `look at window` to see the detail
- ✅ Perfect for environmental flavor that can't be manipulated
- ✅ Can't be picked up or moved (unlike real objects)

**Alternative Pattern (if @detail is problematic in batch files):**
Create examinable objects instead:
```bash
@create window:typeclasses.objects.ExaminableObject
@desc window = A grimy window streaked with rain.
@set window/fixed = True
@tel window = Detective Office
```

---

## Typeclasses Explained

### What is a Typeclass?

A **typeclass** is Python class that defines the behavior and properties of an object. It's Evennia's way of creating different "types" of objects with custom functionality.

**Think of it like:**
- Class inheritance in OOP
- A "template" or "blueprint" for objects
- A way to add custom code to objects

### Typeclass Hierarchy

```
DefaultObject          ← Evennia core
    ↓
ObjectParent          ← Your game's shared mixin (typeclasses/objects.py)
    ↓
Object                ← Base game object
    ↓
MagicalWeapon         ← Your custom typeclass
```

### Creating Custom Typeclasses

**File location:** `typeclasses/objects.py` or `typeclasses/rooms.py`

```python
from typeclasses.objects import Object

class ReadableObject(Object):
    """
    An object that can be read like a letter or book.
    """
    def at_object_creation(self):
        """Called once when object is first created"""
        self.db.read_text = "There is nothing written here."

    def return_appearance(self, looker, **kwargs):
        """What the object looks like"""
        text = super().return_appearance(looker, **kwargs)
        text += "\n|y(You could 'read' this)|n"
        return text
```

**Using in batch file:**
```bash
@create mysterious letter:typeclasses.objects.ReadableObject
@set letter/read_text = The letter contains a cryptic message...
```

### Important Typeclass Hooks

**Hooks** are methods Evennia calls at specific times. Override them to add custom behavior:

```python
def at_object_creation(self):
    """Called once when object is created"""
    # Set default attributes
    self.db.health = 100

def at_object_receive(self, moved_obj, source_location, **kwargs):
    """Called when another object enters this object"""
    # Example: Trap room that triggers when entered
    if moved_obj.is_character:
        moved_obj.msg("You triggered a trap!")

def at_before_move(self, destination, **kwargs):
    """Called before object moves. Return False to prevent move"""
    if self.db.rooted:
        self.msg("You are rooted in place!")
        return False
    return True

def at_after_move(self, source_location, **kwargs):
    """Called after successful move"""
    self.msg(f"You have arrived at {self.location.name}")

def return_appearance(self, looker, **kwargs):
    """What the object looks like when examined"""
    text = super().return_appearance(looker, **kwargs)
    # Add custom text
    return text + "\nSomething seems special about this."
```

### Common Custom Typeclasses

**Extended Room (with @detail support):**
```python
# typeclasses/rooms.py
from evennia.contrib.grid.extended_room import ExtendedRoom

class NoirRoom(ExtendedRoom):
    """
    Room with atmospheric details and mood.
    """
    def at_object_creation(self):
        super().at_object_creation()
        self.db.mood = "neutral"
        self.db.light = "normal"

    def return_appearance(self, looker, **kwargs):
        text = super().return_appearance(looker, **kwargs)
        if self.db.mood:
            text += f"\n|xThe atmosphere feels {self.db.mood}.|n"
        return text
```

**Readable Object:**
```python
# typeclasses/objects.py
from typeclasses.objects import Object

class ReadableObject(Object):
    """
    An object with readable text.
    """
    def at_object_creation(self):
        super().at_object_creation()
        self.db.read_text = "Nothing is written here."
```

**Container Object:**
```python
# typeclasses/objects.py
from typeclasses.objects import Object

class Container(Object):
    """
    An object that can hold other objects.
    """
    def at_object_creation(self):
        super().at_object_creation()
        self.db.capacity = 10
        self.locks.add("get:false()")  # Can't be picked up
```

---

## Attributes System

### What are Attributes?

**Attributes** are persistent key-value pairs stored on objects. They survive server reboots and can hold any Python data type.

**Access patterns:**
```python
# In Python code
obj.db.attribute_name = value
value = obj.db.attribute_name

# In batch files
@set obj/attribute_name = value
```

### Attribute Categories

Attributes can have categories for organization:

```bash
# Set attribute with category
@set obj/attribute_name[category] = value

# Example
@set sword/damage[combat] = 10
@set sword/name[original] = Excalibur
```

### Viewing Attributes

```bash
# View single attribute
@set obj/attribute_name

# View all attributes on object
@examine obj
```

### Common Attribute Patterns

**Room atmosphere:**
```bash
@set Room/light = dim
@set Room/smell = musty air
@set Room/ambient_sound = dripping water
@set Room/temperature = cold
@set Room/mood = foreboding
```

**Object properties:**
```bash
@set Object/value = 100
@set Object/weight = 5.5
@set Object/material = steel
@set Object/condition = worn
@set Object/description_extra = Additional flavor text
```

**Quest flags:**
```bash
@set Object/quest_item = True
@set Object/quest_id = "main_quest_01"
@set Object/quest_stage = 3
```

**NPC data:**
```bash
@set NPC/health = 100
@set NPC/max_health = 100
@set NPC/disposition = friendly
@set NPC/dialogue_state = greeting
```

### Built-in Attributes

Some attributes have special meaning in Evennia:

| Attribute | Purpose | Set By |
|-----------|---------|--------|
| `desc` | Object description (from `look`) | `@desc` or `@set obj/desc` |
| `get_text` | Message when object picked up | `@set obj/get_text` |
| `drop_text` | Message when object dropped | `@set obj/drop_text` |
| `aliases` | Alternative names for object | `@alias` |

---

## Object Hierarchy & Properties

### Object Properties vs Attributes

**Properties** are defined in Python code and are typically read-only or managed by Evennia.
**Attributes** are set via `@set` and store custom game data.

**Properties (read-only in batch files):**
- `obj.id` - Database ID (#15, #203, etc.)
- `obj.key` - Primary name
- `obj.location` - Where the object is
- `obj.typeclass_path` - Python class defining behavior
- `obj.locks` - Lock string controlling permissions

**Attributes (writable in batch files):**
- `obj.db.desc` - Description text
- `obj.db.custom_value` - Any custom data
- `obj.db.*` - Any attribute you create

### Object Relationships

```
Room (#15)
  ├── Exit "north" (#16) ──> Other Room (#20)
  ├── Exit "south" (#17) ──> Third Room (#21)
  ├── Character "Player" (#18)
  └── Object "sword" (#19)
```

**In Python:**
```python
# Get room's contents
room.contents  # [Exit, Exit, Character, Object]

# Get room's exits specifically
room.exits  # [Exit, Exit]

# Get exit's destination
exit.destination  # Other Room (#20)

# Get object's location
obj.location  # Room (#15)
```

---

## Exits and Room Connectivity

### How Exits Work

An **Exit** is a one-way object connecting two rooms. Exits have:
- **Location** - The room they exit FROM (source)
- **Destination** - The room they lead TO (target)
- **Key** - The name of the exit ("north", "door", etc.)
- **Aliases** - Alternative names ("n", "wooden door", etc.)

### Creating Bidirectional Travel

To allow travel in both directions, create TWO exits:

```bash
# Room A → Room B
@open north;n:Room A = Room B

#

# Room B → Room A
@open south;s:Room B = Room A

#
```

### Exit Naming Conventions

**Standard compass directions:**
```bash
north;n
south;s
east;e
west;w
northeast;ne
northwest;nw
southeast;se
southwest;sw
up;u
down;d
in;i
out;o
```

**Custom exit names:**
```bash
@open wooden door;door = Office

#

@open secret passage;passage;hidden door = Chamber

#

@open ladder;climb ladder = Attic

#
```

### Exit Direction Conflicts

⚠️ **IMPORTANT:** A room can only have ONE exit with a given name.

**Example of CONFLICT:**
```bash
# Room A → Room B (creates "north" exit from A)
@open north;n:Room A = Room B

#

# This creates ANOTHER "north" exit from Room A - CONFLICT!
@open north;n:Room A = Room C  # ✗ Room A now has TWO "north" exits!

#
```

**How to avoid:**
- Plan your map topology before building
- Use unique direction names for each exit from a room
- For complex connections, use custom exit names

**Solution - Plan your map:**
```bash
# Entrance → Hub (use "in/out")
@open in;enter:Entrance = Hub
@open out;exit:Hub = Entrance

#

# Hub → North Wing (use "north/south")
@open north;n:Hub = North Wing
@open south;s:North Wing = Hub

#

# Hub → East Wing (use "east/west")
@open east;e:Hub = East Wing
@open west;w:East Wing = Hub

#

# No conflicts!
```

### Linking Existing Rooms

Use `@open` to connect rooms that already exist:

```bash
# Create rooms in Phase 1
@create Library:evennia.objects.objects.DefaultRoom
@create Secret Room:evennia.objects.objects.DefaultRoom

#

# Later in Phase 3, connect them
@open bookshelf;shelf:Library = Secret Room
@open back:Secret Room = Library

#
```

---

## Locks and Permissions

### What are Locks?

**Locks** control who can do what to an object. They are rule strings that Evennia evaluates to determine permissions.

### Default Lock Strings

When you create an object with `@create`, Evennia automatically assigns these locks:

```
control:pid(123) or id(456) or perm(Admin)
delete:pid(123) or id(456) or perm(Admin)
edit:pid(123) or id(456) or perm(Admin)
```

Where:
- `pid(123)` - Player/Account ID who created the object
- `id(456)` - Character ID that created the object
- `perm(Admin)` - Anyone with Admin permission

**Note:** The audit mentioned these locks include `pid()` and `id()` access, which is correct.

### Common Lock Types

| Lock Type | Controls |
|-----------|----------|
| `control` | Who can change locks on object |
| `delete` | Who can delete object |
| `edit` | Who can edit object properties |
| `get` | Who can pick up object |
| `drop` | Who can drop object |
| `view` | Who can see object exists |
| `examine` | Who can see object details |

### Setting Locks in Batch Files

```bash
@lock <object> = <lock type>:<lock function>
```

**Examples:**
```bash
# Make object pickable by anyone
@lock sword = get:all()

#

# Make object only pickable by admins
@lock sword = get:perm(Admin)

#

# Make object unpickable (like furniture)
@lock desk = get:false()

#

# Make object only visible to certain players
@lock secret_door = view:perm(Builder) or id(123)

#

# Multiple locks at once
@lock sword = get:all();drop:all();examine:perm(Builder)

#
```

### Common Lock Functions

| Function | Meaning |
|----------|---------|
| `all()` | Everyone |
| `false()` | No one |
| `true()` | Everyone (same as `all()`) |
| `perm(Admin)` | Anyone with Admin permission |
| `perm(Builder)` | Anyone with Builder permission |
| `id(123)` | Specific character by ID |
| `pid(456)` | Specific account/player by ID |

### Checking Locks

```bash
# View object's locks
@examine object

# Test if you can pass a lock
@access object = locktype
```

---

## Python API for Batch Code

### When to Use Batch-Code vs Batch-Command

**Batch-Command files (.ev):**
- Use game commands like `@create`, `@open`, `@desc`
- Good for simple world building
- Easy for LLMs to generate
- Recommended for most use cases

**Batch-Code files (.py):**
- Use Python API directly
- Good for complex logic, calculations, procedural generation
- Requires Python knowledge
- More powerful but more error-prone

### Basic Python API Examples

**Creating objects:**
```python
from evennia import create_object

# Create a room
room = create_object(
    "evennia.objects.objects.DefaultRoom",
    key="Detective Office"
)

# Create an object
sword = create_object(
    "typeclasses.objects.MagicalWeapon",
    key="Excalibur",
    location=room,
    aliases=["sword", "blade"]
)

# Set attributes
room.db.desc = "A cramped office thick with smoke."
room.db.mood = "noir"
sword.db.damage = 10
```

**Creating exits:**
```python
from evennia import create_object

# Create exit from room1 to room2
exit_north = create_object(
    "evennia.objects.objects.DefaultExit",
    key="north",
    location=room1,
    destination=room2,
    aliases=["n"]
)

# Create return exit
exit_south = create_object(
    "evennia.objects.objects.DefaultExit",
    key="south",
    location=room2,
    destination=room1,
    aliases=["s"]
)
```

**Finding objects:**
```python
from evennia import search_object

# Search by name
results = search_object("Detective Office")
if results:
    room = results[0]

# Search within a container
results = search_object("sword", candidates=room.contents)

# Search by typeclass
from evennia.objects.models import ObjectDB
rooms = ObjectDB.objects.filter(
    db_typeclass_path__contains="DefaultRoom"
)
```

**Setting locks:**
```python
# Set locks on object
obj.locks.add("get:all()")
obj.locks.add("drop:all()")

# Check if object passes lock
can_get = obj.access(character, "get")
```

---

## Common Patterns Explained

### The Standard Room Build Pattern

**Phase 1: Create rooms**
```bash
@create Room 1:evennia.objects.objects.DefaultRoom
@create Room 2:evennia.objects.objects.DefaultRoom
@create Room 3:evennia.objects.objects.DefaultRoom

#
```

**Phase 2: Describe rooms**
```bash
@desc Room 1 = Description here...

#

@set Room 1/light = dim
@set Room 1/mood = tense

#

@desc Room 2 = Another description...

#

@set Room 2/light = bright

#
```

**Phase 3: Create exits**
```bash
@open north;n:Room 1 = Room 2
@open south;s:Room 2 = Room 1

#

@open east;e:Room 2 = Room 3
@open west;w:Room 3 = Room 2

#
```

### The Hub-and-Spoke Pattern

**Create a central hub with multiple branches:**

```bash
# Create hub and all spoke rooms
@create Town Square:evennia.objects.objects.DefaultRoom
@create North Gate:evennia.objects.objects.DefaultRoom
@create South Gate:evennia.objects.objects.DefaultRoom
@create East Market:evennia.objects.objects.DefaultRoom
@create West Temple:evennia.objects.objects.DefaultRoom

#

# Describe them all...
@desc Town Square = The bustling center of town...

#

# Create exits - hub to spokes
@open north;n:Town Square = North Gate
@open south;s:Town Square = South Gate
@open east;e:Town Square = East Market
@open west;w:Town Square = West Temple

#

# Create exits - spokes back to hub
@open south;s:North Gate = Town Square
@open north;n:South Gate = Town Square
@open west;w:East Market = Town Square
@open east;e:West Temple = Town Square

#
```

### The Linear Path Pattern

**Create a sequence of connected rooms:**

```bash
# Create all rooms
@create Entrance:evennia.objects.objects.DefaultRoom
@create Hallway:evennia.objects.objects.DefaultRoom
@create Chamber:evennia.objects.objects.DefaultRoom
@create Exit:evennia.objects.objects.DefaultRoom

#

# Connect them in sequence
@open in;enter:Entrance = Hallway
@open out;back:Hallway = Entrance

#

@open forward;ahead:Hallway = Chamber
@open back;retreat:Chamber = Hallway

#

@open exit;leave:Chamber = Exit
@open back;return:Exit = Chamber

#
```

### The Object Creation Pattern

**Create objects and place them in rooms:**

```bash
# Create the object
@create ornate key;key:typeclasses.objects.QuestItem

#

# Describe it
@desc ornate key = A brass key with intricate engravings.

#

# Set attributes
@set ornate key/value = 100
@set ornate key/quest_id = "main_quest_01"

#

# Place it in a room
@tel ornate key = Detective Office

#
```

### The ExtendedRoom Pattern

**Using ExtendedRoom with @detail:**

```bash
# Create ExtendedRoom
@create Detective Office:evennia.contrib.grid.extended_room.ExtendedRoom

#

# Describe it
@desc Detective Office =
  A cramped office thick with cigarette smoke.

#

# Teleport to it
@tel Detective Office

#

# Add details (must be IN the room)
@detail desk = A battered oak desk covered in case files.

#

@detail window = Rain streaks the dirty window.

#

@detail ashtray = An overflowing ashtray, still smoldering.

#
```

---

## Troubleshooting & Best Practices

### Best Practices for Batch Files

**DO:**
- ✅ Use stateless commands (@create, @open, @desc, @set)
- ✅ Follow the three-phase pattern
- ✅ Use explicit room names, never "here"
- ✅ Terminate multi-line commands with `#`
- ✅ Use blank lines for readability
- ✅ Add comments explaining complex sections
- ✅ Test incrementally with small builds first

**DON'T:**
- ❌ Use @dig or @tunnel in batch files
- ❌ Rely on @tel for navigation
- ❌ Use `@desc here` (use room name)
- ❌ Create exit direction conflicts
- ❌ Forget the `#` terminator on multi-line commands

### Common Errors and Solutions

**Error: "You cannot create an exit from a None-location"**
- **Cause:** Using @dig or @open without proper context
- **Solution:** Use explicit source room syntax: `@open exit:RoomName = Destination`

**Error: "More than one match for 'RoomName'"**
- **Cause:** Duplicate rooms with same name
- **Solution:** Delete duplicates or use unique names

**Error: "Command not found: @detail"**
- **Cause:** ExtendedRoom contrib not installed
- **Solution:** Enable contrib in settings or use regular objects

**Error: "Destination not found"**
- **Cause:** Typo in room name or room doesn't exist
- **Solution:** Double-check room names, ensure rooms created before exits

**Error: Exit direction conflicts**
- **Cause:** Two exits from same room with same direction name
- **Solution:** Plan map topology to avoid conflicts, use unique directions

### Debugging Batch Files

**Test incrementally:**
```bash
# Test Phase 1 only
@batchcommand test_phase1

# If that works, test Phase 2
@batchcommand test_phase2

# Then Phase 3
@batchcommand test_phase3
```

**Use @examine to inspect objects:**
```bash
@examine Room Name
# Shows: ID, typeclass, location, attributes, locks
```

**Check exit connectivity:**
```bash
@examine exit_name
# Shows: destination, aliases
```

**Find objects by ID:**
```bash
look #123
@examine #123
```

### Performance Tips

**For large builds (100+ rooms):**
- Split into multiple batch files by area
- Run during off-peak hours
- Test with small sample first
- Use batch-code (.py) for procedural generation

**Batch file size limits:**
- No hard limit, but 500-1000 commands is reasonable
- Larger files take longer to execute
- Consider splitting very large builds

---

## Interactive Building Commands (Not for Batch Files)

⚠️ **These commands are for INTERACTIVE, HUMAN building only. Do NOT use in LLM-generated batch files.**

The following commands are stateful - they depend on your current location and move you around as side effects. While useful for human builders exploring and creating interactively, they cause problems in batch files:

- Navigation can fail, breaking the build
- Hard to debug and understand
- Creates fragile, order-dependent scripts
- Confuses LLM reasoning about spatial relationships

**For reference only - use @create + @open instead.**

### @dig - Creating Rooms with Exits (STATEFUL - AVOID)

**Syntax:**
```bash
@dig <room name>[;room aliases] =
  <exit to there>[;exit aliases],
  <exit back here>[;exit aliases]
```

**What it does:**
1. Creates a new Room
2. Creates two Exits (bidirectional connection)
3. Links exits to appropriate destinations
4. Leaves you in your current location (use `/teleport` switch to move into the new room)

**Why not to use in batch files:**
- Depends on current location (stateful)
- Implicitly creates exits instead of explicitly naming them
- Hard to see topology from reading the file
- Navigation failures break the build

**Example (for reference):**
```bash
@dig Detective's Office;office = door;wooden door, hall;hallway
```

This creates:
- Room: "Detective's Office" (alias: "office")
- Exit from current location → office: "door" (alias: "wooden door")
- Exit from office → current location: "hall" (alias: "hallway")
- You remain in your current location

**Use instead:**
```bash
# Stateless alternative
@create Detective's Office;office:evennia.objects.objects.DefaultRoom
@open door;wooden door:Current Room = Detective's Office
@open hall;hallway:Detective's Office = Current Room
```

### @tunnel - Create and Traverse (STATEFUL - AVOID)

**Syntax:**
```bash
@tunnel[/tel] <direction> = <room name>
```

**What it does:**
- Creates an exit in the specified direction
- Creates a NEW room at the destination
- Creates a return exit automatically
- Leaves you in your current location (use `/tel` switch to move)

**Why not to use in batch files:**
- Only works with standard compass directions
- Depends on current location (stateful)
- Limited to simple, grid-based layouts
- Fails with complex room names
- Navigation (`@tel`) can fail in batch context

**Limitations:**
1. Only accepts: `n, s, e, w, ne, nw, se, sw, u, d, in, out`
2. Switch is `/tel` NOT `/teleport`
3. Room names with spaces/special characters cause issues
4. Always creates NEW room (can't connect to existing)

**Example (for reference):**
```bash
@tunnel north = DarkForest
# Creates: exit "north" → room "DarkForest"
# Creates: exit "south" → your previous room
```

**Use instead:**
```bash
# Stateless alternative
@create Dark Forest:evennia.objects.objects.DefaultRoom
@open north;n:Current Room = Dark Forest
@open south;s:Dark Forest = Current Room
```

### @teleport (@tel) - Moving Objects (STATEFUL - AVOID)

**Syntax:**
```bash
@teleport[/quiet] [<object> =] <destination>
```

**What it does:**
Moves an object to a new location.

**Why not to use in batch files:**
- Navigation can fail (typo in room name, room doesn't exist yet)
- When navigation fails, subsequent commands build from wrong location
- Creates order-dependent, fragile scripts
- Not needed with stateless @create + @open approach

**Example (for reference):**
```bash
# Teleport yourself
@tel Limbo

# Teleport an object
@tel sword = Armory
```

**Use instead:**
```bash
# Stateless alternative for placing objects
@create sword:typeclasses.objects.Weapon
@desc sword = A gleaming blade.
@tel sword = Armory  # This is OK for object placement, not navigation
```

**Acceptable use:** `@tel` is acceptable for placing objects in rooms (not for navigating yourself), since object placement doesn't affect the build topology:
```bash
# This is OK - placing an object
@tel object_name = Room Name
```

---

## Summary: Commands by Use Case

### For Batch Files (Stateless - Use These)

| Command | Use For |
|---------|---------|
| `@create` | Creating rooms and objects |
| `@open` | Creating exits between rooms |
| `@desc` | Setting descriptions |
| `@set` | Setting attributes |
| `@detail` | Adding room details (with @tel if needed) |
| `@lock` | Setting permissions |
| `@alias` | Adding alternative names |

### For Interactive Building Only (Stateful - Avoid in Batch Files)

| Command | Why Avoid |
|---------|-----------|
| `@dig` | Stateful - depends on location, implicit exits |
| `@tunnel` | Stateful - depends on location, limited directions |
| `@tel` | Stateful - navigation can fail |

---

**End of Technical Reference**

For practical examples and templates, see: `Evennia-Batch-Build-Examples.md`
