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