from evennia import AttributeProperty, CmdSet, default_cmds
from evennia.commands.command import Command, InterruptCommand
from evennia.utils.utils import (
    display_len,
    inherits_from,
    list_to_string,
    pad,
    repeat,
    unrepeat,
)

from .characters import TestAdvCharacter
from .combat_base import (
    CombatActionAttack,
    CombatActionHold,
    CombatActionStunt,
    CombatActionUseItem,
    CombatActionWield,
    TestAdvCombatBaseHandler,
)
from .enums import ABILITY_REVERSE_MAP


class TestAdvCombatTwitchHandler(TestAdvCombatBaseHandler):
    '''
    This is created on the combatant when combat starts. It tracks only the combatants
    side of the combat and handles the next action that will happen.
    '''
    advantage_against = AttributeProperty(dict)
    disadvantage_against = AttributeProperty(dict)

    action_classes = {
        "hold": CombatActionHold,
        "attack": CombatActionAttack,
        "stunt": CombatActionStunt,
        "use": CombatActionUseItem,
        "wield": CombatActionWield,
    }

    action_dict = AttributeProperty(dict, autocreate=False)
    fallback_action_dict = AttributeProperty({"key": "hold", "dt": 0})

    #stores the current ticker ref
    current_ticker_ref = AttributeProperty(None, autocreate=False)

    def msg(self, message, broadcast=True):
        '''
        see TestAdvCombatBaseHandler.msg
        '''
        super().msg(message, combatant=self.obj, broadcast=broadcast, location=self.obj.location)

    def get_sides(self, combatant):
        '''
        get a listing of the two sides of combat, from the perspective of the combatant
        
        args:
            combatant (character or NPC): basis for the sides
            
        Returns:
            tuple: a tuple of lists (allies, enemies), from the perspective of 'combatant'
            Combatant is not included in either list.
        '''
        # get all entities in combat by looking up their combat handlers.
        combatants = [
            comb
            for comb in self.obj.location.contents
            if hasattr(comb, "scripts") and comb.scripts.has(self.key)
        ]
        location = self.obj.location

        if hasattr(location, "allow_pvp") and location.allow_pvp:
            # in pvp, everyone else is an enemy
            allies = [combatant]
            enemies = [comb for comb in combatants if comb != combatant]
        else: 
            # otherwise, enemies/allies depend on who the combatant is
            pcs = [comb for comb in combatants if inherits_from(comb, TestAdvCharacter)]
            npcs = [comb for comb in combatants if comb not in pcs]
            if combatant in pcs:
                # combatant is a PC, so all NPCs are enemies
                allies = pcs
                enemies = npcs
            else:
                # combatant is an NPC, so all PCs are enemies
                allies = npcs
                enemies = pcs
        return allies, enemies
    
    def give_advantage(self, recipient, target):
        '''
        Let a recipient gain advantage against a target
        '''
        self.advantage_against[target] = True

    def give_disadvantage(self, recipient, target):
        '''
        Let's an affected party gain disadvantage against a target.
        '''
        self.disadvantage_against[target] = True

    def has_advantage(self, combatant, target):
        '''
        Check if the combatant has advantage against the target
        '''
        return self.advantage_against.get(target, False)

    def has_disadvantage(self, combatant, target):
        '''
        Check if the combatant has disadvantage against a target.
        '''
        return self.disadvantage_against.get(target, False)
    
    def queue_action(self, action_dict, combatant=None):
        '''
        Schedule the next action to fire.
        
        Args:
            action_dict (dict): the new action-dict to initialize.
            combatant (optional): Unused.
        '''
        if action_dict["key"] not in self.action_classes:
            self.obj.msg("This is an unknown action!")
            return
        
        # store action dict and schedule it to run in dt time
        self.action_dict = action_dict
        dt = action_dict.get("dt", 0)

        if self.current_ticker_ref:
            # if we have a ticker going, abort it
            unrepeat(self.current_ticker_ref)
        if dt <= 0:
            # no repeat
            self.current_ticker_ref = None
        else: 
            # always schedule the task to be repeating, cancel later otherwise.
            # We store the tickerhandler's ref to make sure we can remove it later
            self.current_ticker_ref= repeat(
                dt, self.execute_next_action, id_string="combat")
            
    def execute_next_action(self):
        '''
        Triggered after a delay by the command
        '''
        combatant = self.obj
        action_dict = self.action_dict
        action_class = self.action_classes[action_dict["key"]]
        action = action_class(self, combatant, action_dict)

        if action.can_use():
            action.execute()
            action.post_execute()

        if not action_dict.get("repeat", True):
            # not a repeating action, use the fallback (normally the original attack)
            self.action_dict = self.fallback_action_dict
            self.queue_action(self.fallback_action_dict)

        self.check_stop_combat()

    def check_stop_combat(self):
        '''
        Check if combat is over.
        '''
        allies, enemies = self.get_sides(self.obj)

        location = self.obj.location

        # Eliminate from consideration any allies or enemies that are alive and in the same room
        allies = [comb for comb in allies if comb.hp > 0 and comb.location == location]
        enemies = [comb for comb in enemies if comb.hp > 0 and comb.location == location]

        # Check if either or both sides have been wiped out
        if not allies and not enemies:
            self.msg("You are slain, as are your enemies.", broadcast=False)
            self.stop_combat()
        if not allies:
            self.msg("YOU DIED.")
            self.stop_combat()
        if not enemies:
            self.msg("None remain who oppose you.")
            self.stop_combat()

    def stop_combat(self):
        pass # TODO apparently we're saving this for last