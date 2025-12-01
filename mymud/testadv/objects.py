from evennia import AttributeProperty, DefaultObject, search_object, create_object 
from evennia.utils.utils import make_iter
from .utils import get_obj_stats 
from .enums import Ability, WieldLocation, ObjType
from . import rules

_BARE_HANDS = None

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
            self.tags.add(obj_type.value, category="obj_type")

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
    # TODO stop from selling or dropping these
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

        # your opposed_saving_throw function returns three values (is_hit, quality, txt).
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
            from_obj=attacker,              # This is a clarification for FuncParser, to help it conjugate
            mapping={target.key: target},   # same here
        )
        if is_hit:
            # enemy hit, calculate damage
            dmg = rules.dice.roll(self.damage_roll)

            if quality is Ability.CRITICAL_SUCCESS:
                # We double the damage for crits
                dmg += rules.dice.roll(self.damage_roll)
                message = (
                    f" $You() |ycritically|n $conj(hit) $You({target.key}) for |r{dmg}|n damage!"
                )
            else:
                message = f" $You() $conj(hit) $You({target.key}) for |r{dmg}|n damage!"

            location.msg_contents(message, from_obj=attacker, mapping={target.key: target})
            # call hook to cause damage to the target
            target.at_damage(dmg, attacker=attacker)

        else:
            # at this point, we've missed
            message = f" $You() $conj(miss) $You({target.key})."
            # truly beansed it, in this case
            if quality is Ability.CRITICAL_FAILURE:
                message += "... it's a |rcritical miss!|n, damaging the weapon."
                # damage the weapon
                if self.quality is not None:
                    self.quality -= 1
                location.msg_contents(message, from_obj=attacker, mapping={target.key: target})

    def at_post_use(self, user, *args, **kwargs):
        # Break the weapon if quality hit zero
        if self.quality is not None and self.quality <= 0:
            user.msg(f"|r{self.get_display_name(user)} breaks and can no longer be used!")


class TestAdvRuneStone(TestAdvWeapon, TestAdvConsumable):
    '''
    Base for all magical rune stones
    Must be wielded in both hands to used
    Can only be used once per rest
    '''
    obj_type = (ObjType.WEAPON, ObjType.MAGIC)
    inventory_use_slot = WieldLocation.TWO_HANDS
    quality = AttributeProperty(3, autocreate=False)

    attack_type = AttributeProperty(Ability.REAS, autocreate=False)
    defense_type = AttributeProperty(Ability.WILL, autocreate=False)

    damage_roll = AttributeProperty("1d8", autocreate=False)

    def at_post_use(self, user, *args, **kwargs):
        # Called after spell is cast
        self.uses -= 1

    def refresh(self):
        # Refresh the rune stone, normally after resting
        self.uses = 1


class TestAdvArmor(TestAdvObject):
    # Armor will be the mother of helmets and shields AND body armor
    #low unarmored characters have 11 base defense
    armor = AttributeProperty(1, autocreate=False)
    quality = AttributeProperty(3, autocreate=False)


class TestAdvBodyArmor(TestAdvArmor):
    # a class specifically for body armor so we can change the armor value independently
    obj_type = ObjType.ARMOR
    inventory_use_slot = WieldLocation.BODY


class TestAdvShield(TestAdvArmor):
    obj_type = ObjType.SHIELD
    inventory_use_slot = WieldLocation.SHIELD_HAND


class TestAdvHelmet(TestAdvArmor):
    obj_type = ObjType.HELMET
    inventory_use_slot = WieldLocation.HEAD


class WeaponBareHands(TestAdvWeapon):
    '''
    we have weapons at home
    '''
    obj_type = ObjType.WEAPON
    inventory_use_slot = WieldLocation.WEAPON_HAND
    attack_type = Ability.PHYS
    defense_type = Ability.ARMOR
    damage_roll = "1d4" # No monks in Knave, I guess
    quality = None      # We're assuming fists are indescructible, even thought it would be REALLY funny

def get_bare_hands():
    '''
    Get the bare hands
    '''
    global _BARE_HANDS
    if not _BARE_HANDS:
        _BARE_HANDS = search_object("Bare Hands", typeclass=WeaponBareHands).first()
    if not _BARE_HANDS:
        _BARE_HANDS = create_object(WeaponBareHands, key="Bare Hands")
    return _BARE_HANDS