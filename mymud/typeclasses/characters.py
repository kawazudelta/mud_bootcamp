"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent

import random

class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    # def at_object_creation(self):
    #     self.db.strength = random.randint(3, 18)
    #     self.db.dexterity = random.randint(3, 18)
    #     self.db.intelligence = random.randint(3, 18)

    # def get_stats(self):
    #     """
    #     Get the main stats of this character
    #     """
    #     return self.db.strength, self.db.dexterity, self.db.intelligence

    def at_pre_move(self, destination, **kwargs):
        '''
        Called by self.move_to when trying to move somcwhere. If this returns False, the move is immediately cancelled.
        '''
        if self.db.is_sitting:
            self.msg("You need to stand up first.")
            return False
        return True