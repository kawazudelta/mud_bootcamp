# Tutorial: implementing Random Loot Tables

**Prerequisites:**
*   You have read the [Evennia Spawner](https://www.evennia.com/docs/latest/Components/Prototypes.html) documentation (or trust me on how it works).
*   You have `testadv/random_tables.py` populated with lists of item names.
*   You have `world/prototypes.py` populated with matching prototype keys.

---

## 1. The Concept: "Weighted Lists & Spawners"

In a MUD, "Loot" is just an Object spawned at a location. A "Loot Table" is just a fancy way of saying "Pick one string from this list."

We already have the lists in `testadv/random_tables.py`.
We already have the item definitions in `world/prototypes.py`.

**The missing link** is a script that:
1.  Takes a table name (e.g., "dungeoning gear").
2.  Rolls a die to pick an entry.
3.  Tells Evennia: "Spawn the object with this prototype key at this location."

---

## 2. The Logic: `world/loot_tables.py`

We will create a new file to handle this logic. This keeps our "Game Rules" separate from our "Data Lists."

**Create File:** `world/loot_tables.py`

```python
import random
from evennia.prototypes.spawner import spawn
from testadv import random_tables

def get_random_loot_prototype(table_name):
    """
    Pick a random prototype key from a list in random_tables.py.
    
    Args:
        table_name (str): The key in random_tables.chargen_tables (e.g., "dungeoning gear")
        
    Returns:
        str: The prototype key (e.g., "rope, 50ft") or None if table not found.
    """
    # Access the dictionary in random_tables
    table = random_tables.chargen_tables.get(table_name)
    
    if not table:
        return None
        
    # Pick a random item
    # Note: Our tables currently look like ["rope", "torch"] 
    # OR tuples like [("1-3", "dagger"), ("4-6", "club")]
    
    choice = random.choice(table)
    
    # Check if it's a tuple (weighted/ranged entry) or a simple string
    if isinstance(choice, tuple):
        # It's a tuple like ("1-3", "dagger"). We just want the name "dagger".
        return choice[1]
    
    # It's just a string
    return choice

def spawn_loot(location, table_name):
    """
    Spawns a random item from the given table at the location.
    """
    proto_key = get_random_loot_prototype(table_name)
    
    if not proto_key:
        return None
        
    # The spawner returns a list of spawned objects (usually just one)
    # We pass the prototype key and the location to spawn it at.
    spawned_objs = spawn(proto_key, location=location)
    
    if spawned_objs:
        return spawned_objs[0]
    return None
```

### Explanation
*   `random.choice(table)`: This is standard Python. It picks one element from a list.
*   `isinstance(choice, tuple)`: Some of our tables (like "starting weapon") are tuples because they have dice ranges `("1-5", "dagger")`. We handle both simple lists and these tuples.
*   `spawn(proto_key, location=location)`: This is the Evennia magic. It looks up the key in `world/prototypes.py`, builds the object, and places it.

---

## 3. The Interface: Testing with a Command

We can't rely on code existing in a vacuum. We need to run it. Let's make a builder command to spawn loot on demand.

**Modify File:** `commands/mycommands.py`

Add this class to the bottom of the file:

```python
# Import the new module we just made
from world import loot_tables

class CmdLoot(default_cmds.MuxCommand):
    """
    Spawn random loot.
    
    Usage:
      loot <table>
      
    Tables:
      dungeoning gear, general gear 1, general gear 2, starting weapon
    """
    key = "loot"
    locks = "cmd:perm(Builder)" # Only builders should use this

    def func(self):
        if not self.args:
            self.caller.msg("Usage: loot <table name>")
            return
            
        table_name = self.args.strip()
        
        # Call our logic function
        obj = loot_tables.spawn_loot(self.caller.location, table_name)
        
        if obj:
            self.caller.msg(f"Spawned: {obj.key} from table '{table_name}'")
        else:
            self.caller.msg(f"Could not spawn loot from table '{table_name}'. Does it exist?")
```

**Register the Command:**
Don't forget to add `CmdLoot` to your `MyCmdSet` class in `commands/mycommands.py`:

```python
class MyCmdSet(CmdSet):
    def at_cmdset_creation(self):
        # ... existing commands ...
        self.add(CmdLoot)
```

---

## 4. Try It Out

1.  **Reload the server:** `reload` (to load the new code).
2.  **Run the command:**
    *   `loot dungeoning gear` -> Should drop a rope or torch.
    *   `loot starting weapon` -> Should drop a dagger or club.
    *   `loot garbage` -> Should tell you the table doesn't exist.

---

## 5. Challenges for You

1.  **Weighted Tables:** Currently, `starting weapon` has ranges like "1-7" for dagger and "8-13" for club. `random.choice` treats them as equal probability (33% chance for each entry). Can you modify `get_random_loot_prototype` to parse the "1-7" string and respect the probability?
2.  **Gold:** Create a "treasure" table that spawns a Pile of Gold object with a random value.

