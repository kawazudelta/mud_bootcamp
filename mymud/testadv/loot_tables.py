import random
from evennia.prototypes.spawner import spawn
from testadv import random_tables
from testadv.rules import dice

def get_random_loot_prototype(table_name):
    '''
    Pick a random prototype key from a list in random_tables.py.
    
    Args:
        table_name (str): The key in random_tables.chargen_tables (e.g., "dungeoning gear")
        
    Returns:
        str: The prototype key (e.g., "rope, 50ft") or None if table not found.
    '''
    # Access the dictionary in random_tables
    table = random_tables.chargen_tables.get(table_name)

    if not table:
        return None
    
    # Pick a random item from the selected table
    # Note: Our tables currently look like ["rope", "torch"] 
    # OR tuples like [("1-3", "dagger"), ("4-6", "club")]

    # Determine die size, and whether we're looking at a weighted list
    # So if the first item on the table is a tuple...
    if isinstance(table[0], tuple):
        # It's a weighted table, we need to calculate the range
        # Get the last range value from the table...
        last_range = table[-1][0]
        # Split the last range around the hyphen, take the second value
        max_val = last_range.split("-")[-1]
        # Set the dire size to that number
        die_string = f"1d{max_val}"
    else:
        # Just a list of strings? Just count how many.
        die_string = f"1d{len(table)}"

    # kick the die string over to our table rolling method and return it
    return dice.roll_random_table(die_string, table)

def spawn_loot(location, table_name):
    '''
    spawns a random item from the given table at the location.
    '''
    proto_key = get_random_loot_prototype(table_name)

    if not proto_key:
        return None
    
    # We create a temporary prototype that inherits from the chosen key
    # and explicitly sets the location. This ensures the spawner handles it correctly.
    spawn_def = {
        "prototype_parent": proto_key,
        "location": location
    }
    
    spawned_objs = spawn(spawn_def)

    if spawned_objs:
        return spawned_objs[0]
    return None