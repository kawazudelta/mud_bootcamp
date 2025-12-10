from commands.command import Command
from evennia import CmdSet
from evennia import default_cmds
from testadv.enums import WieldLocation
from testadv import loot_tables

class CmdEquip(default_cmds.MuxCommand):
    """
    view equipped items

    Usage:
      equip
      eq

    Shows your currently worn and wielded equipment.
    """
    key = "equip"
    aliases = ["eq"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        
        if not hasattr(caller, "equipment"):
            caller.msg("You have no equipment slots.")
            return

        # Get all items from the handler
        all_items = caller.equipment.all()
        
        # Filter for equipped items
        equipped = []
        for item, slot in all_items:
            if not item:
                continue
            if slot != WieldLocation.BACKPACK:
                # Format slot name nicely
                slot_name = slot.value.replace("_", " ").title()
                equipped.append(f"  |w{slot_name:<15}|n: {item.get_display_name(caller)}")

        # Build output
        output = [f"|c=== Equipment for {caller.key} ===|n"]
        if equipped:
            output.extend(equipped)
        else:
            output.append("  You are not wearing anything.")
        output.append(f"|c================================|n")

        caller.msg("\n".join(output))

class CmdInventory(default_cmds.MuxCommand):
    """
    view inventory

    Usage:
      inventory
      inv
      i

    Shows your backpack contents.
    """
    key = "inventory"
    aliases = ["inv", "i"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        
        if not hasattr(caller, "equipment"):
            caller.msg("You have no inventory.")
            return

        # Get all items from the handler
        all_items = caller.equipment.all()
        
        # Filter for backpack items
        backpack = []
        for item, slot in all_items:
            if not item:
                continue
            if slot == WieldLocation.BACKPACK:
                backpack.append(item)

        # Build output
        output = [f"|c=== Inventory for {caller.key} ===|n"]
        if backpack:
            output.append(f"|wBackpack ({len(backpack)}/{caller.equipment.max_slots} slots):|n")
            for item in backpack:
                output.append(f"  {item.get_display_name(caller)}")
        else:
            output.append("|wBackpack:|n Empty")
        output.append(f"|c================================|n")

        caller.msg("\n".join(output))

class CmdEcho(default_cmds.MuxCommand):
    """
    Simple command that always sends text back to the caller.
    """
    key = "echo"
    locks = "cmd:all()"

    def func(self):
        self.caller.msg(f"Echo: {self.args}")


class CmdHit(Command):
    '''
    Hit a target.
    
    Usage:
        hit <target>
    '''
    key = "hit"

    def parse(self):
        self.args = self.args.strip()
        target, *weapon = self.args.split(" with ", 1)
        if not weapon:
            target, *weapon = target.split(" ", 1)
        self.target = target.strip()
        if weapon:
            self.weapon = weapon[0].strip()
        else:
            self.weapon = ""

    def func(self):
        if not self.args:
            self.caller.msg("Who do you want to hit?")
            return
        # get the target for the hit
        target = self.caller.search(self.target)
        if not target:
            return
        # get and handle the weapon
        weapon = None
        if self.weapon:
            weapon = self.caller.search(self.weapon)
        if weapon:
            weaponstr = f"{weapon.key}"
        else:
            weaponstr = "bare fists"

        self.caller.msg(f"You hit {target.key} with {weaponstr}!")
        target.msg(f"You got hit by {self.caller.key} with {weaponstr}!")


class CmdLook(default_cmds.CmdLook):
    """
    look at location or object

    Usage:
      look
      look <obj>
      look *<account>

    Observes your location or objects in your vicinity.
    """
    
    def func(self):
        """
        Handle the looking.
        """
        caller = self.caller
        
        # If we have args, check if the player is trying to look at something they are wearing.
        if self.args and hasattr(caller, "equipment"):
            # Get all equipped items
            equip_items = [item for item, slot in caller.equipment.all() if item]
            
            # Search strictly within equipment
            # quiet=True returns a list of matches, not the object itself
            target = caller.search(self.args, candidates=equip_items, quiet=True)
            
            if target:
                # We found a match (or matches) in the equipment!
                # We handle the first match found, just like standard search.
                # (Note: caller.search returns a list of objects when quiet=True)
                obj = target[0] 
                self.msg(caller.at_look(obj))
                return

        # If we didn't find it in equipment, or had no args, let standard Look handle it.
        # This preserves 'look here', 'look *account', and standard room/inventory looking.
        super().func()


class MyCmdGet(default_cmds.CmdGet):

    def func(self):
        super().func()
        self.caller.msg(str(self.caller.location.contents))


class CmdCharCreate(Command):
    """
    Start the character generation process.

    Usage:
        charcreate
    """
    key = "charcreate"
    aliases = ["@charcreate"]

    def func(self):
        from testadv.chargen import start_chargen
        start_chargen(self.caller, self.session)


class CmdTestLoot(default_cmds.MuxCommand):
    '''
    Spawn random loot.

    Usage:
        testloot <table>
      
    Tables:
        dungeoning gear, general gear 1, general gear 2, starting weapon
    '''
    key = "testloot"
    locks = "cmd:perm(Builder)"

    def func(self):
        if not self.args:
            table_name = "loot"
        else:
            table_name = self.args.strip()
        
        # Debug: check location
        loc = self.caller.location
        
        obj = loot_tables.spawn_loot(loc, table_name)

        if obj:
            self.caller.msg(f"Spawned {obj.key} from table '{table_name}'.")
        else:
            self.caller.msg(f"Could not spawn loot from table '{table_name}'.")


class CmdWield(default_cmds.MuxCommand):
    """
    Wield or wear an item.

    Usage:
      wield <obj>
      wear <obj>

    Equips an item from your backpack into its proper slot.
    """
    key = "wield"
    aliases = ["wear"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Wield what?")
            return
        
        if not hasattr(caller, "equipment"):
            caller.msg("You can't wield anything.")
            return

        # Find the item. Standard search finds things in inventory/backpack.
        obj = caller.search(self.args)
        if not obj:
            return
        
        # Try to move it to its slot
        # We assume move() returns True on success, False on failure (as we updated it)
        if caller.equipment.move(obj):
            caller.msg(f"You equip {obj.get_display_name(caller)}.")
        else:
            caller.msg("You can't equip that.")


class CmdRemove(default_cmds.MuxCommand):
    """
    Remove an equipped item.

    Usage:
      remove <obj>
      unequip <obj>
      unwield <obj>

    Takes an item from a worn slot and places it in your backpack.
    """
    key = "remove"
    aliases = ["unequip", "unwield"]
    locks = "cmd:all()"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Remove what?")
            return
        
        if not hasattr(caller, "equipment"):
            caller.msg("You have nothing to remove.")
            return

        # Custom search for EQUIPPED items only
        # We don't want to find things in the room or backpack
        equip_items = [item for item, slot in caller.equipment.all() if item and slot != WieldLocation.BACKPACK]
        
        # Use quiet search to get a list of matches
        matches = caller.search(self.args, candidates=equip_items, quiet=True)
        
        if not matches:
            caller.msg("You don't have that equipped.")
            return
        
        # If multiple matches, we handle it simply for now (pick first)
        # or we could ask for clarification.
        if len(matches) > 1:
             # If exact match exists in the list, prefer it
             # This mimics standard Evennia logic loosely
             exact_matches = [m for m in matches if m.key.lower() == self.args.lower()]
             if exact_matches:
                 obj = exact_matches[0]
             else:
                 caller.msg("Multiple items found. Please be more specific.")
                 return
        else:
            obj = matches[0]
        
        # Perform the move: Remove from slot, Add to backpack
        # remove() returns a list of removed objects
        removed_objs = caller.equipment.remove(obj)
        if obj in removed_objs:
            # Successfully removed, now put in backpack
            caller.equipment.add(obj)
            caller.msg(f"You unequip {obj.get_display_name(caller)}.")
        else:
            caller.msg("Could not remove the item.")


class MyCmdSet(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdEcho)
        self.add(CmdHit)
        self.add(CmdCharCreate)
        self.add(CmdTestLoot)
        self.add(CmdWield)
        self.add(CmdRemove)