"""
Prototypes

A prototype is a simple way to create individualized instances of a
given typeclass. It is dictionary with specific key names.

For example, you might have a Sword typeclass that implements everything a
Sword would need to do. The only difference between different individual Swords
would be their key, description and some Attributes. The Prototype system
allows to create a range of such Swords with only minor variations. Prototypes
can also inherit and combine together to form entire hierarchies (such as
giving all Sabres and all Broadswords some common properties). Note that bigger
variations, such as custom commands or functionality belong in a hierarchy of
typeclasses instead.

A prototype can either be a dictionary placed into a global variable in a
python module (a 'module-prototype') or stored in the database as a dict on a
special Script (a db-prototype). The former can be created just by adding dicts
to modules Evennia looks at for prototypes, the latter is easiest created
in-game via the `olc` command/menu.

Prototypes are read and used to create new objects with the `spawn` command
or directly via `evennia.spawn` or the full path `evennia.prototypes.spawner.spawn`.

A prototype dictionary have the following keywords:

Possible keywords are:
- `prototype_key` - the name of the prototype. This is required for db-prototypes,
  for module-prototypes, the global variable name of the dict is used instead
- `prototype_parent` - string pointing to parent prototype if any. Prototype inherits
  in a similar way as classes, with children overriding values in their parents.
- `key` - string, the main object identifier.
- `typeclass` - string, if not set, will use `settings.BASE_OBJECT_TYPECLASS`.
- `location` - this should be a valid object or #dbref.
- `home` - valid object or #dbref.
- `destination` - only valid for exits (object or #dbref).
- `permissions` - string or list of permission strings.
- `locks` - a lock-string to use for the spawned object.
- `aliases` - string or list of strings.
- `attrs` - Attributes, expressed as a list of tuples on the form `(attrname, value)`,
  `(attrname, value, category)`, or `(attrname, value, category, locks)`. If using one
   of the shorter forms, defaults are used for the rest.
- `tags` - Tags, as a list of tuples `(tag,)`, `(tag, category)` or `(tag, category, data)`.
-  Any other keywords are interpreted as Attributes with no category or lock.
   These will internally be added to `attrs` (equivalent to `(attrname, value)`.

See the `spawn` command and `evennia.prototypes.spawner.spawn` for more info.

"""

## example of module-based prototypes using
## the variable name as `prototype_key` and
## simple Attributes

# from random import randint
#
# GOBLIN = {
# "key": "goblin grunt",
# "health": lambda: randint(20,30),
# "resists": ["cold", "poison"],
# "attacks": ["fists"],
# "weaknesses": ["fire", "light"],
# "tags": = [("greenskin", "monster"), ("humanoid", "monster")]
# }
#
# GOBLIN_WIZARD = {
# "prototype_parent": "GOBLIN",
# "key": "goblin wizard",
# "spells": ["fire ball", "lighting bolt"]
# }
#
# GOBLIN_ARCHER = {
# "prototype_parent": "GOBLIN",
# "key": "goblin archer",
# "attacks": ["short bow"]
# }
#
# This is an example of a prototype without a prototype
# (nor key) of its own, so it should normally only be
# used as a mix-in, as in the example of the goblin
# archwizard below.
# ARCHWIZARD_MIXIN = {
# "attacks": ["archwizard staff"],
# "spells": ["greater fire ball", "greater lighting"]
# }
#
# GOBLIN_ARCHWIZARD = {
# "key": "goblin archwizard",
# "prototype_parent" : ("GOBLIN_WIZARD", "ARCHWIZARD_MIXIN")
# }

from testadv.enums import WieldLocation, Ability, ObjType
# We use string paths for typeclasses to avoid circular imports if those files import prototypes (unlikely but safe)
# Actually, standard practice in prototypes.py is often just dicts, but importing Enums is fine.

# --- WEAPONS ---

DAGGER = {
    "prototype_key": "dagger",
    "key": "dagger",
    "typeclass": "testadv.objects.TestAdvWeapon",
    "damage_roll": "1d6",
    "desc": "A sharp, double-edged fighting knife."
}

CLUB = {
    "prototype_key": "club",
    "key": "club",
    "typeclass": "testadv.objects.TestAdvWeapon",
    "damage_roll": "1d6",
    "desc": "A heavy wooden stick."
}

STAFF = {
    "prototype_key": "staff",
    "key": "staff",
    "typeclass": "testadv.objects.TestAdvWeapon",
    "inventory_use_slot": WieldLocation.TWO_HANDS,
    "damage_roll": "1d6",
    "desc": "A long, sturdy wooden pole."
}

# --- ARMOR ---

GAMBESON = {
    "prototype_key": "gambeson",
    "key": "gambeson",
    "typeclass": "testadv.objects.TestAdvBodyArmor",
    "armor": 1,
    "desc": "A padded defensive jacket."
}

BRIGANDINE = {
    "prototype_key": "brigandine",
    "key": "brigandine",
    "typeclass": "testadv.objects.TestAdvBodyArmor",
    "armor": 2,
    "desc": "Cloth armor reinforced with internal metal plates."
}

CHAIN = {
    "prototype_key": "chain",
    "key": "chainmail",
    "typeclass": "testadv.objects.TestAdvBodyArmor",
    "armor": 3,
    "desc": "Armor made of interlocking metal rings."
}

HELMET = {
    "prototype_key": "helmet",
    "key": "helmet",
    "typeclass": "testadv.objects.TestAdvHelmet",
    "armor": 1,
    "desc": "A metal helm to protect the head."
}

SHIELD = {
    "prototype_key": "shield",
    "key": "shield",
    "typeclass": "testadv.objects.TestAdvShield",
    "armor": 1,
    "desc": "A wooden or metal shield."
}

# --- DUNGEONING GEAR ---

ROPE = {
    "prototype_key": "rope, 50ft",
    "key": "rope",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "50 feet of sturdy hemp rope."
}

PULLEYS = {
    "prototype_key": "pulleys",
    "key": "pulleys",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A set of wooden pulleys."
}

CANDLES = {
    "prototype_key": "candles, 5",
    "key": "candles",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A bundle of 5 wax candles."
}

CHAIN_10FT = {
    "prototype_key": "chain, 10ft",
    "key": "chain",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "10 feet of iron chain."
}

CHALK = {
    "prototype_key": "chalk, 10",
    "key": "chalk",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "10 sticks of white chalk."
}

CROWBAR = {
    "prototype_key": "crowbar",
    "key": "crowbar",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A solid iron crowbar."
}

TINDERBOX = {
    "prototype_key": "tinderbox",
    "key": "tinderbox",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "Flint, steel, and tinder for starting fires."
}

GRAP_HOOK = {
    "prototype_key": "grap. hook",
    "key": "grappling hook",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "An iron hook with a rope loop."
}

HAMMER = {
    "prototype_key": "hammer",
    "key": "hammer",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A small hammer for pitons or carpentry."
}

WATERSKIN = {
    "prototype_key": "waterskin",
    "key": "waterskin",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A leather pouch for water."
}

LANTERN = {
    "prototype_key": "lantern",
    "key": "lantern",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A hooded oil lantern."
}

LAMP_OIL = {
    "prototype_key": "lamp oil",
    "key": "lamp oil",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A flask of oil."
}

PADLOCK = {
    "prototype_key": "padlock",
    "key": "padlock",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A heavy iron padlock with a key."
}

MANACLES = {
    "prototype_key": "manacles",
    "key": "manacles",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "Iron cuffs for restraining a prisoner."
}

MIRROR = {
    "prototype_key": "mirror",
    "key": "mirror",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A small steel mirror."
}

POLE = {
    "prototype_key": "pole, 10ft",
    "key": "pole",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A 10-foot wooden pole."
}

SACK = {
    "prototype_key": "sack",
    "key": "sack",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A burlap sack."
}

TENT = {
    "prototype_key": "tent",
    "key": "tent",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "A simple canvas tent."
}

SPIKES = {
    "prototype_key": "spikes, 5",
    "key": "spikes",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "5 iron spikes."
}

TORCHES = {
    "prototype_key": "torches, 5",
    "key": "torches",
    "typeclass": "testadv.objects.TestAdvObject",
    "desc": "5 bundles of pitch-soaked wood."
}

# --- GENERAL GEAR 1 ---

AIR_BLADDER = { "prototype_key": "air bladder", "key": "air bladder", "typeclass": "testadv.objects.TestAdvObject" }
BEAR_TRAP = { "prototype_key": "bear trap", "key": "bear trap", "typeclass": "testadv.objects.TestAdvObject" }
SHOVEL = { "prototype_key": "shovel", "key": "shovel", "typeclass": "testadv.objects.TestAdvObject" }
BELLOWS = { "prototype_key": "bellows", "key": "bellows", "typeclass": "testadv.objects.TestAdvObject" }
GREASE = { "prototype_key": "grease", "key": "grease", "typeclass": "testadv.objects.TestAdvObject" }
SAW = { "prototype_key": "saw", "key": "saw", "typeclass": "testadv.objects.TestAdvObject" }
BUCKET = { "prototype_key": "bucket", "key": "bucket", "typeclass": "testadv.objects.TestAdvObject" }
CALTROPS = { "prototype_key": "caltrops", "key": "caltrops", "typeclass": "testadv.objects.TestAdvObject" }
CHISEL = { "prototype_key": "chisel", "key": "chisel", "typeclass": "testadv.objects.TestAdvObject" }
DRILL = { "prototype_key": "drill", "key": "drill", "typeclass": "testadv.objects.TestAdvObject" }
FISH_ROD = { "prototype_key": "fish. rod", "key": "fishing rod", "typeclass": "testadv.objects.TestAdvObject" }
MARBLES = { "prototype_key": "marbles", "key": "bag of marbles", "typeclass": "testadv.objects.TestAdvObject" }
GLUE = { "prototype_key": "glue", "key": "glue", "typeclass": "testadv.objects.TestAdvObject" }
PICK = { "prototype_key": "pick", "key": "mining pick", "typeclass": "testadv.objects.TestAdvObject" }
HOURGLASS = { "prototype_key": "hourglass", "key": "hourglass", "typeclass": "testadv.objects.TestAdvObject" }
NET = { "prototype_key": "net", "key": "net", "typeclass": "testadv.objects.TestAdvObject" }
TONGS = { "prototype_key": "tongs", "key": "tongs", "typeclass": "testadv.objects.TestAdvObject" }
LOCKPICKS = { "prototype_key": "lockpicks", "key": "lockpicks", "typeclass": "testadv.objects.TestAdvObject" }
METAL_FILE = { "prototype_key": "metal file", "key": "metal file", "typeclass": "testadv.objects.TestAdvObject" }
NAILS = { "prototype_key": "nails", "key": "bag of nails", "typeclass": "testadv.objects.TestAdvObject" }

# --- GENERAL GEAR 2 ---

INCENSE = { "prototype_key": "incense", "key": "incense", "typeclass": "testadv.objects.TestAdvObject" }
SPONGE = { "prototype_key": "sponge", "key": "sponge", "typeclass": "testadv.objects.TestAdvObject" }
LENS = { "prototype_key": "lens", "key": "lens", "typeclass": "testadv.objects.TestAdvObject" }
PERFUME = { "prototype_key": "perfume", "key": "perfume", "typeclass": "testadv.objects.TestAdvObject" }
HORN = { "prototype_key": "horn", "key": "horn", "typeclass": "testadv.objects.TestAdvObject" }
BOTTLE = { "prototype_key": "bottle", "key": "bottle", "typeclass": "testadv.objects.TestAdvObject" }
SOAP = { "prototype_key": "soap", "key": "soap", "typeclass": "testadv.objects.TestAdvObject" }
SPYGLASS = { "prototype_key": "spyglass", "key": "spyglass", "typeclass": "testadv.objects.TestAdvObject" }
TAR_POT = { "prototype_key": "tar pot", "key": "tar pot", "typeclass": "testadv.objects.TestAdvObject" }
TWINE = { "prototype_key": "twine", "key": "twine", "typeclass": "testadv.objects.TestAdvObject" }
FAKE_JEWELS = { "prototype_key": "fake jewels", "key": "fake jewels", "typeclass": "testadv.objects.TestAdvObject" }
BLANK_BOOK = { "prototype_key": "blank book", "key": "blank book", "typeclass": "testadv.objects.TestAdvObject" }
CARD_DECK = { "prototype_key": "card deck", "key": "deck of cards", "typeclass": "testadv.objects.TestAdvObject" }
DICE_SET = { "prototype_key": "dice set", "key": "set of dice", "typeclass": "testadv.objects.TestAdvObject" }
COOK_POTS = { "prototype_key": "cook pots", "key": "cooking pots", "typeclass": "testadv.objects.TestAdvObject" }
FACE_PAINT = { "prototype_key": "face paint", "key": "face paint", "typeclass": "testadv.objects.TestAdvObject" }
WHISTLE = { "prototype_key": "whistle", "key": "whistle", "typeclass": "testadv.objects.TestAdvObject" }
INSTRUMENT = { "prototype_key": "instrument", "key": "musical instrument", "typeclass": "testadv.objects.TestAdvObject" }
QUILL_INK = { "prototype_key": "quill & ink", "key": "quill and ink", "typeclass": "testadv.objects.TestAdvObject" }
SMALL_BELL = { "prototype_key": "small bell", "key": "small bell", "typeclass": "testadv.objects.TestAdvObject" }

# --- CONSUMABLES ---

RATION = {
    "prototype_key": "ration",
    "key": "ration",
    "typeclass": "testadv.objects.TestAdvConsumable",
    "desc": "A slightly stale but nourishing ration.",
    "uses": 1
}
