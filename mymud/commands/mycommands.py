from commands.command import Command
from evennia import CmdSet
from evennia import default_cmds
from testadv.enums import WieldLocation

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


class MyCmdSet(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdEcho)
        self.add(CmdHit)
        self.add(CmdCharCreate)