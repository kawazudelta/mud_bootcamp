from evennia import DefaultCharacter, AttributeProperty

from .characters import LivingMixin
from .enums import Ability
from .objects import get_bare_hands

class TestAdvNPC(LivingMixin, DefaultCharacter):
    '''
    Base class for NPCS
    '''
    is_pc = False
    hit_dice = AttributeProperty(default=1, autocreate=False)
    armor = AttributeProperty(default=11, autocreate=False) # we have to use the whole armor value here, not just the bonus
    hp_multiplier = AttributeProperty(default=4, autocreate=False)  # 4 is the default in knave
    hp = AttributeProperty(default=None, autocreate=False)  # internal tracking, use .hp property
    morale = AttributeProperty(default=9, autocreate=False)
    allegiance = AttributeProperty(default=Ability.ALLEGIANCE_HOSTILE, autocreate=False)

    weapon = AttributeProperty(default=get_bare_hands, autocreate=False)    # instead of inventory
    coins = AttributeProperty(default=1, autocreate=False)

    is_idle = AttributeProperty(default=False, autocreate=False)

    @property
    def physique(self):
        # we have to change the formula again because we're tracking total stats, not bonuses
        return 10 + self.hit_dice
    
    @property
    def coordination(self):
        return 10 + self.hit_dice

    @property
    def instinct(self):
        return 10 + self.hit_dice

    @property
    def reason(self):
        return 10 + self.hit_dice

    @property
    def willpower(self):
        return 10 + self.hit_dice

    @property
    def auspice(self):
        return 10 + self.hit_dice

    @property
    def max_hp(self):
        return self.hit_dice * self.hp_multiplier
    
    def at_object_creation(self):
        '''
        NPCs start with max health
        '''
        self.hp = self.max_hp
        self.tags.add("npcs", category="group")


class TestAdvMob(TestAdvNPC):
    '''
    A mobile enemy
    '''
    




