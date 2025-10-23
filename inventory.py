# inventory.py
# A simple module to store and display a player's items.

inventory = {} # now a dictionary, not a list

def add_item(item, qty=1):
    """Add an item and increase its count."""
    inventory[item] = inventory.get(item, 0) + qty
    print(f"Added {qty} x {item} (total: {inventory[item]})")
    save_inventory

def remove_item(item, qty=1):
    """Remove an item (Or reduce its count)."""
    if item in inventory:
        inventory[item] -= qty
        if inventory[item] <= 0:
            del inventory[item]
            print(f"{item} removed from inventory.")
        else:
            print(f"Removed {qty} x {item} (remaining): {inventory[item]})")
    else:
        print(f"You don't have any {item}.")
    save_inventory

def show_inventory():
    """Show everything you're carrying."""
    if not inventory:
        print("Your inventory is empty.")
    else:
        print("\ninventory:")
        for item, qty in inventory.items():
            print(f"- {item} (x{qty})")

def has_item(item):
    """check if player has a specific item"""
    return item in inventory

import json
from pathlib import Path

# where the save file will live (same folder)
SAVE_FILE = Path("inventory_save.json")

def save_inventory():
    """Write the inventory dictionary to a JSON file."""    
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2)
    print(f"[DEBUG] Inventory saved to {SAVE_FILE.resolve()}")

def load_inventory():
    """Load the inventory dictionary from file, if it exists."""
    global inventory
    if SAVE_FILE.exists():
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                inventory = json.load(f)
            print("[DEBUG] Inventory loaded from file.")
        except json.JSONDecodeError:
            print("[DEBUG] Save file corrupted - starting fresh.")
            inventory = {}
    else:
        inventory = {}
        print("[DEBUG] No save file found - starting fresh.")