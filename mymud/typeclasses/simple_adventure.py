"""
Simple Adventure Module
=======================

This module implements a clean, simplified set of "Adventure" features 
compatible with the TestAdv game system. It replaces the legacy 
TutorialWorld code with a robust, easier-to-maintain implementation.

Features:
- WeatherRoom: Echoes atmospheric messages.
- DarkRoom: Requires a light source to see.
- LightSource: An item that can be lit.
- TeleportRoom: Moves players based on keys/tags.
- PatrolMob: An NPC that wanders and attacks.

Inheritance:
- Objects inherit from testadv.objects.TestAdvObject
- Rooms inherit from testadv.rooms.TestAdvRoom
- Mobs inherit from testadv.npcs.TestAdvMob
"""

import random
from evennia import CmdSet, Command, TICKER_HANDLER, syscmdkeys, search_object
from evennia.utils import delay
from testadv.objects import TestAdvObject
from testadv.rooms import TestAdvRoom
from testadv.npcs import TestAdvMob
from testadv.enums import ObjType, WieldLocation

# ----------------------------------------------------------------------------
# WEATHER ROOM
# ----------------------------------------------------------------------------

class AdventureWeatherRoom(TestAdvRoom):
    """
    A room that periodically echoes weather messages to its contents.
    
    Attributes:
        weather_msgs (list): List of strings to echo randomly.
        weather_interval (int): Seconds between checks (default ~60).
        weather_chance (float): Chance (0.0-1.0) to echo on a tick.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.weather_msgs = [
            "A cold wind blows through.",
            "Dust swirls in the air.",
            "You hear a distant dripping sound."
        ]
        self.db.weather_interval = 60
        self.db.weather_chance = 0.3
        
        # Start the ticker
        self.start_weather_ticker()

    def start_weather_ticker(self):
        """Starts the ticker."""
        # Randomize interval slightly to prevent all rooms echoing at once
        interval = self.db.weather_interval + random.randint(-10, 10)
        TICKER_HANDLER.add(
            interval=interval, 
            callback=self.update_weather, 
            idstring=f"weather_{self.id}"
        )

    def update_weather(self, *args, **kwargs):
        """Called by ticker."""
        if random.random() < (self.db.weather_chance or 0.3):
            msgs = self.db.weather_msgs
            if msgs:
                self.msg_contents(f"|w{random.choice(msgs)}|n")

# ----------------------------------------------------------------------------
# LIGHT SOURCE
# ----------------------------------------------------------------------------

class CmdLight(Command):
    """
    Light a light source.
    Usage: light <object>
    """
    key = "light"
    aliases = ["burn", "ignite"]
    locks = "cmd:all()" # Logic handled in func

    def func(self):
        # We target the object holding the command set
        obj = self.obj
        
        if obj.db.is_lit:
            self.caller.msg(f"{obj.key} is already lit.")
            return
            
        if not obj.location == self.caller:
            self.caller.msg("You need to hold it to light it.")
            return

        self.caller.msg(f"You light {obj.key}.")
        self.caller.location.msg_contents(f"{self.caller.key} lights {obj.key}.")
        obj.light()

class CmdExtinguish(Command):
    """
    Put out a light source.
    Usage: extinguish <object>
    """
    key = "extinguish"
    aliases = ["put out", "douse"]
    
    def func(self):
        obj = self.obj
        if not obj.db.is_lit:
            self.caller.msg(f"{obj.key} is not lit.")
            return
        
        self.caller.msg(f"You extinguish {obj.key}.")
        obj.extinguish()

class AdventureLightSource(TestAdvObject):
    """
    An object that creates light.
    
    Attributes:
        fuel (int): How many seconds it lasts (default 300).
        is_lit (bool): Current state.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.obj_type = ObjType.GEAR
        self.db.is_lit = False
        self.db.fuel = 300 
        self.db.desc_lit = "It glows brightly."
        self.db.desc_unlit = "It is dark and cold."
        
        # Add commands
        self.cmdset.add(CmdSetLight, persistent=True)

    def return_appearance(self, looker, **kwargs):
        base = super().return_appearance(looker, **kwargs)
        state = "|y(Lit)|n" if self.db.is_lit else "|x(Unlit)|n"
        return f"{base}\n{state}"

    def light(self):
        """Turn on."""
        self.db.is_lit = True
        # Force a light check in the current room
        if self.location:
            self.location.msg_contents(f"{self.key} flares to life.")
            # If we are in a DarkRoom, update it
            room = self.location.location if self.location.has_account else self.location
            if hasattr(room, "check_light_state"):
                room.check_light_state()

    def extinguish(self):
        """Turn off."""
        self.db.is_lit = False
        if self.location:
            room = self.location.location if self.location.has_account else self.location
            if hasattr(room, "check_light_state"):
                room.check_light_state()

class CmdSetLight(CmdSet):
    key = "light_source_cmdset"
    def at_cmdset_creation(self):
        self.add(CmdLight())
        self.add(CmdExtinguish())

# ----------------------------------------------------------------------------
# DARK ROOM
# ----------------------------------------------------------------------------

class CmdDarkLook(Command):
    """
    Look command used when in the dark.
    """
    key = "look"
    aliases = ["l", "search", "feel"]
    locks = "cmd:all()"
    
    def func(self):
        caller = self.caller
        # Small chance to find something?
        # For now, just generic message.
        caller.msg("It is pitch black. You are likely to be eaten by a grue.")

class CmdDarkNoMatch(Command):
    """
    Catch-all for commands in the dark.
    """
    key = syscmdkeys.CMD_NOMATCH
    locks = "cmd:all()"
    
    def func(self):
        self.caller.msg("It is too dark to do that!")

class DarkCmdSet(CmdSet):
    """
    Active when the room is dark.
    """
    key = "dark_room_cmdset"
    priority = 5 # High priority to override default look
    mergetype = "Replace" 
    
    def at_cmdset_creation(self):
        self.add(CmdDarkLook())
        self.add(CmdDarkNoMatch())
        # We must explicitly allow important system commands to pass through
        from evennia.commands.default import general, system
        self.add(general.CmdQuit())
        self.add(general.CmdHome())
        self.add(general.CmdSay())

class AdventureDarkRoom(TestAdvRoom):
    """
    A room that is dark unless a light source is present.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.is_dark = True
        self.cmdset.add(DarkCmdSet, persistent=True)
    
    def at_init(self):
        self.check_light_state()

    def _has_light(self):
        """
        Check if there is a light source in the room.
        """
        # 1. Check objects on the floor
        for obj in self.contents:
            if obj.db.is_lit: 
                return True
        
        # 2. Check characters' inventories
        for obj in self.contents:
            if obj.has_account: # It's a player/mob
                for item in obj.contents:
                    if item.db.is_lit:
                        return True
                        
        # 3. Superusers are bioluminescent
        for obj in self.contents:
            if obj.is_superuser:
                return True
                
        return False

    def check_light_state(self):
        """
        Updates the room's command set based on light.
        """
        has_light = self._has_light()
        
        if has_light:
            # Remove dark restrictions
            self.cmdset.remove(DarkCmdSet)
            self.locks.add("view:all()")
            # Notify
            if self.db.is_dark: # State change
                self.msg_contents("The room is illuminated.")
                self.db.is_dark = False
        else:
            # Apply dark restrictions
            self.cmdset.add(DarkCmdSet, persistent=True)
            self.locks.add("view:false()")
            if not self.db.is_dark: # State change
                self.msg_contents("The light fades. It is pitch black.")
                self.db.is_dark = True

    def at_object_receive(self, obj, source_location, move_type="move", **kwargs):
        super().at_object_receive(obj, source_location, move_type=move_type, **kwargs)
        # Check if the new arrival brought light
        self.check_light_state()

    def at_object_leave(self, obj, target_location, move_type="move", **kwargs):
        super().at_object_leave(obj, target_location, move_type=move_type, **kwargs)
        # Check if light left with them
        self.check_light_state()

# ----------------------------------------------------------------------------
# TELEPORT ROOM
# ----------------------------------------------------------------------------

class AdventureTeleportRoom(TestAdvRoom):
    """
    Teleports players based on a 'key' item or tag.
    
    Attributes:
        puzzle_key (str): Key of the object or Tag name required.
        target_success (str): Name/Dbref of room if key is found.
        target_failure (str): Name/Dbref of room if key missing.
        msg_success (str): Message on success.
        msg_failure (str): Message on failure.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.puzzle_key = None
        self.db.target_success = None
        self.db.target_failure = None
        self.db.msg_success = "The way is open."
        self.db.msg_failure = "The way is closed."

    def at_object_receive(self, obj, source_location, move_type="move", **kwargs):
        if not obj.has_account:
            return
            
        super().at_object_receive(obj, source_location, move_type=move_type, **kwargs)
        
        # Don't trigger on build commands
        if obj.ndb.batch_batchmode:
            return

        key = self.db.puzzle_key
        if not key:
            return # No puzzle set up

        # Check if user has key
        has_key = False
        
        # Check Inventory
        if any(o.key.lower() == key.lower() for o in obj.contents):
            has_key = True
        # Check Tags
        elif obj.tags.get(key, category="tutorial"):
            has_key = True
            
        target = self.db.target_success if has_key else self.db.target_failure
        msg = self.db.msg_success if has_key else self.db.msg_failure
        
        if not target:
            return
            
        # Find target room
        results = search_object(target)
        if not results:
            obj.msg(f"|rTeleport Error: Destination '{target}' not found.|n")
            return
            
        destination = results[0]
        
        # Execute
        obj.msg(msg)
        obj.move_to(destination, move_type="teleport")

# ----------------------------------------------------------------------------
# PATROL MOB
# ----------------------------------------------------------------------------

class AdventurePatrolMob(TestAdvMob):
    """
    An NPC that patrols and attacks.
    Inherits combat stats from TestAdvMob.
    """
    
    def at_object_creation(self):
        super().at_object_creation()
        self.db.patrol_interval = 10
        self.db.is_aggressive = True
        
        # Start patrolling
        self.start_patrol()

    def start_patrol(self):
        TICKER_HANDLER.add(
            interval=self.db.patrol_interval,
            callback=self.do_patrol_tick,
            idstring=f"patrol_{self.id}"
        )

    def do_patrol_tick(self, *args, **kwargs):
        """
        Called every tick.
        1. Check for enemies.
        2. If none, move.
        """
        if not self.location:
            return

        # 1. Look for targets
        targets = [
            o for o in self.location.contents 
            if o.has_account and not o.is_superuser
        ]
        
        if targets and self.db.is_aggressive:
            # Combat logic is handled by TestAdvMob auto-attacking if engaged?
            # Or we initiate it here.
            target = random.choice(targets)
            self.execute_cmd(f"kill {target.key}")
            return

        # 2. Patrol Move
        exits = [e for e in self.location.exits if e.access(self, "traverse")]
        if exits:
            # Prefer an exit we didn't just come from? (Too complex for now)
            # Just random walk
            ex = random.choice(exits)
            self.move_to(ex.destination)

# ----------------------------------------------------------------------------
# INTERACTIVE OBJECTS
# ----------------------------------------------------------------------------

class CmdRead(Command):
    """Read an object."""
    key = "read"
    locks = "cmd:all()"
    def func(self):
        text = self.obj.db.readable_text
        if text:
            self.caller.msg(f"You read {self.obj.key}:\n{text}")
        else:
            self.caller.msg("There is nothing to read.")

class CmdSetReadable(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdRead())

class AdventureReadable(TestAdvObject):
    """An object you can read."""
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add(CmdSetReadable, persistent=True)
        self.db.readable_text = "Blank."

class CmdClimb(Command):
    """Climb an object."""
    key = "climb"
    locks = "cmd:all()"
    def func(self):
        msg = self.obj.db.climb_msg or f"You climb {self.obj.key}."
        self.caller.msg(msg)
        # Set a tag to prove we climbed it
        self.caller.tags.add(f"climbed_{self.obj.id}", category="tutorial")

class CmdSetClimbable(CmdSet):
    def at_cmdset_creation(self):
        self.add(CmdClimb())

class AdventureClimbable(TestAdvObject):
    """An object you can climb."""
    def at_object_creation(self):
        super().at_object_creation()
        self.cmdset.add(CmdSetClimbable, persistent=True)
        self.db.climb_msg = "You climb up."

