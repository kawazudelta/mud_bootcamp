from evennia import AttributeProperty, DefaultObject 
from evennia.utils.utils import make_iter
from .utils import get_obj_stats 
from .enums import Ability, WieldLocation, ObjType
from . import rules

class TestAdvObject(DefaultObject):
    '''
    Parent class for all objects in TestAdv.
    '''
    # default values
    inventory_use_slot = WieldLocation.BACKPACK
    size = AttributeProperty(1, autocreate=False)
    value = AttributeProperty(0, autocreate=False)
    
    # this can be either a single type or a list of types (for objects able to be 
    # act as multiple). This is used to tag this object during creation.
    obj_type = ObjType.GEAR

    # default evennia hooks

    def at_object_creation(self):
        '''
        Called when this object is first created. We convert the .obj_type property to a database tag.
        '''
        # runs a loop through the list of the objects obj_type values and adds them to the object as tags
        for obj_type in make_iter(self.obj_type):
            self.tags.add(self.obj_type.value, category="obj_type")

    def get_display_header(self, looker, **kwargs):
        '''
        The top of the description
        '''
        return ""   # currently empty

    def get_display_desc(self, looker, **kwargs):
        '''
        The main display, show object stats
        '''
        return get_obj_stats(self, owner=looker)

    # custom testadv methods

    def has_obj_type(self, objtype):
        '''
        Check if object is of a certain type
        '''
        return objtype.value in make_iter(self.obj_type)
        
    def at_pre_use(self, *args, **kwargs):
        '''
        Called before use. If returning False, can't be used
        '''
        return True
    
    def use(self, *args, **kwargs):
        '''
        Called when this item is used. That could mean anything.
        '''
        pass
    
    def post_use(self, *args, **kwargs):
        '''
        Called after use.
        '''
        pass

    def get_help(self):
        """Get any help text for this item"""
        return "No help for this item"
    

class TestAdvQuestObject(TestAdvObject):
    '''
    Shouldn't normally be possible to sell or trade these.
    '''
    obj_type = ObjType.QUEST


class TestAdvTreasure(TestAdvObject):
    '''
    Normally only used for selling
    '''
    obj_type = ObjType.TREASURE
    value = AttributeProperty(100, autocreate=False)
    

class TestAdvConsumable(TestAdvObject):
    '''
    an item that can be used up
    '''

    obj_type = ObjType.CONSUMABLE
    value = AttributeProperty(0.25, autocreate=False)
    uses = AttributeProperty(1, autocreate=False)

    def at_pre_use(self, user, target=None, *args, **kwargs):
        '''
        Called before use. If returning False, can't be used
        '''
        if target and user.location != target.location:
            user.msg("You are not close enough to the target!")
            return False
        
        if self.uses <= 0:
            user.msg(f"|w{self.key} is used up.|n")
            return False
        
    def use(self, user, *args, **kwargs):
        '''
        Called when using the item.
        '''
        pass

    def at_post_use(self, user, *args, **kwargs):
        '''
        Called after using the item.
        '''
        self.uses -= 1
        if self.uses <= 0:
            user.msg(f"|w{self.key} is used up.|n")
            self.delete()


class TestAdvWeapon(TestAdvObject):
    '''
    Base class for all weapons
    '''
    obj_type = ObjType.WEAPON
    inventory_use_slot = AttributeProperty(WieldLocation.WEAPON_HAND, autocreate=False)
    quality = AttributeProperty(3, autocreate=False)
    
    attack_type = AttributeProperty(Ability.PHYS, autocreate=False)
    defense_type = AttributeProperty(Ability.ARMOR, autocreate=False)
    
    damage_roll = AttributeProperty("1d6", autocreate=False)
    
    def at_pre_use(self, user, target=None, *args, **kwargs):
        if target and user.location != target.location:
            # weapons can only be used in the same location
            user("You are not close enough to the target!")
            return False
        
        if self.quality is not None and self.quality <= 0:
            user.msg(f"{self.get_display_name(user)} is broken and can't be used!")
            return False
        return super().at_pre_use(user, target=target, *args, **kwargs)
        
    def use(self, attacker, target, *args, attacker_advantage=False, attacker_disadvantage=False, **kwargs):
        '''
        Using a weapon is an attack, generally
        '''
        location = attacker.location

        # your opposed_saving_throw function returns two values (is_hit, quality), not three.
        is_hit, quality, txt = rules.dice.opposed_saving_throw(
            attacker,
            target,
            attack_type=self.attack_type,
            defense_type=self.defense_type,
            attacker_advantage=attacker_advantage,
            attacker_disadvantage=attacker_disadvantage
            # defender's advantage/disadvantage will default to False in the rules function
        )
        location.msg_contents(
            f"$You() $conj(attack) $You({target.key}) with {self.key}: {txt}",
            from_obj=attacker,              # This is a clarification for FuncParser, to help is conjugate
            mapping={target.key: target},   # same here
        )
        if is_hit: