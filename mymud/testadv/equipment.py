from evennia.utils.utils import inherits_from

from .enums import WieldLocation, Ability
from .objects import TestAdvObject, get_bare_hands

class EquipmentError(TypeError):
    '''
    All types of equipment errors
    '''
    pass


class EquipmentHandler:
    # notice no inheritance 
    save_attribute = "inventory_slots"

    def __init__(self, obj):
        # here obj is the character we store the handler on
        self.obj = obj
        self._load()

    def _load(self):
        '''
        Load our data from an Attribute on self.obj
        '''
        self.slots = self.obj.attributes.get(
            self.save_attribute,
            category="inventory",
            default={
                WieldLocation.WEAPON_HAND: None,
                WieldLocation.SHIELD_HAND: None,
                WieldLocation.TWO_HANDS: None,
                WieldLocation.BODY: None,
                WieldLocation.HEAD: None,
                WieldLocation.BACKPACK: []
            }
        )

    def _save(self):
        '''
        Save our data to the same Attribute on self.obj
        '''
        self.obj.attributes.add(self.save_attribute, self.slots, category="inventory")

    @property
    def max_slots(self):
        '''
        Max amount of slots. We deviate from the tutorial/Knave here:
        Inventory slots = Phys + Reas
        How much you can carry physically + how smart you are about packing/distributing the weight
        '''
        phys = getattr(self.obj, Ability.PHYS.value, 1)
        reas = getattr(self.obj, Ability.REAS.value, 1)
        return phys + reas
    
    def count_slots(self):
        '''
        Count how many slots we're using
        '''
        slots = self.slots
        wield_usage = sum(
            getattr(slotobj, "size", 0) or 0
            for slot, slotobj in slots.items()
            if slot is not WieldLocation.BACKPACK
        )
        backpack_usage = sum(
            getattr(slotobj, "size", 0) or 0 for slotobj in slots[WieldLocation.BACKPACK]
        
        )
        return wield_usage + backpack_usage
    
    def validate_slot_usage(self, obj):
        '''
        Check if obj can fit in equipment, based on size
        First check if they can equip it at all
        '''
        if not inherits_from(obj, TestAdvObject):
            # in case we mis with non TestAdv objects
            raise EquipmentError(f"{obj.key} isn't equippable.")
        
        size = obj.size
        max_slots = self.max_slots
        current_slot_usage = self.count_slots()
        return current_slot_usage + size <= max_slots
    
    def add(self, obj):
        '''
        Add an item to the backpack
        '''
        if self.validate_slot_usage(obj):
            self.slots[WieldLocation.BACKPACK].append(obj)
            self._save()

    def remove(self, obj_or_slot):
        '''
        Remove specific object or objects from a slot.
        Returns a list of 0, 1 or more objects removed from inventory.

        obj_or_slot is the argument parsed from the player command (I bet)
        '''
        slots = self.slots
        ret = []
        if isinstance(obj_or_slot, WieldLocation):
            # a slot; if this fails, obj_or_slot must be obj
            if obj_or_slot is WieldLocation.BACKPACK:
                # empty entire backpack
                ret.extend(slots[obj_or_slot])
                slots[obj_or_slot] = []
            else:
                ret.append(slots[obj_or_slot])
                slots[obj_or_slot] = None
        elif obj_or_slot in self.slots.values():
            # obj in use/wear slot
            for slot, objslot in slots.items():
                if objslot is obj_or_slot:
                    slots[slot] = None
                    ret.append(objslot)
        elif obj_or_slot in slots[WieldLocation.BACKPACK]:
            try:
                slots[WieldLocation.BACKPACK].remove(obj_or_slot)
                ret.append(obj_or_slot)
            except ValueError:
                pass
        if ret:
            self._save()
        return ret
    
    def move(self, obj):
        '''
        Move object from backpack to its intended use slot
        '''
        #make sure to remove from equipment/backpack first to avoid double adding
        self.remove(obj)
        if not self.validate_slot_usage(obj):
            return
        
        slots = self.slots
        use_slot = getattr(obj, "inventory_use_slot", WieldLocation.BACKPACK)

        to_backpack = []
        if use_slot is WieldLocation.TWO_HANDS:
            # Two handed weapons preclude a weapon and shield hand item
            to_backpack = [slots[WieldLocation.WEAPON_HAND]], slots[WieldLocation.SHIELD_HAND]
            slots[WieldLocation.WEAPON_HAND] = None
            slots[WieldLocation.SHIELD_HAND] = None
            slots[use_slot] = obj
        elif use_slot in (WieldLocation.WEAPON_HAND, WieldLocation.SHIELD_HAND):
            # Unequip a two handed weapon if you're equipping something one-handed
            to_backpack = [slots[WieldLocation.TWO_HANDS]]
            slots[WieldLocation.TWO_HANDS] = None
            slots[use_slot] = obj
        elif use_slot is WieldLocation.BACKPACK:
            # This guy belongs in the backpack
            to_backpack = [obj]
        else:
            # for anything else (body or head) we just replace it
            to_backback = [slots[use_slot]]
            slots[use_slot] = obj

        for to_backpack_obj in to_backpack:
            # using a loop to put everything back in the backpack
            if to_backpack_obj:
                slots[WieldLocation.BACKPACK].append(to_backpack_obj)
        
        # save the new equipment state
        self._save()

    def all(self):
        '''
        Get all objects in inventory, regardless of location
        '''
        slots = self.slots
        lst = [
            (slots[WieldLocation.WEAPON_HAND], WieldLocation.WEAPON_HAND),
            (slots[WieldLocation.SHIELD_HAND], WieldLocation.SHIELD_HAND),
            (slots[WieldLocation.TWO_HANDS], WieldLocation.TWO_HANDS),
            (slots[WieldLocation.BODY], WieldLocation.BODY),
            (slots[WieldLocation.HEAD], WieldLocation.HEAD),    
        ] + [(item, WieldLocation.BACKPACK) for item in slots[WieldLocation.BACKPACK]]
        return lst

    @property    
    def armor(self):
        slots = self.slots
        return sum(
            (
                # armor is listed using it's defense. Here we deviate again from the tutorial.
                # We just list its bonus. need to set the base 10 armor somewhere else then.
                # TODO figure out where the ten (eleven?) base points of armor go
                getattr(slots[WieldLocation.BODY], "armor", 1)
                # Shields and helmets are listed by the bonus they give to armor
                + getattr(slots[WieldLocation.SHIELD_HAND], "armor", 1)
                + getattr(slots[WieldLocation.HEAD], "armor", 1)
            )
        )
    
    @property
    def weapon(self):
        # check if we're wielding a two-hander, then a one-hander
        # it should never be both
        slots = self.slots
        weapon = slots[WieldLocation.TWO_HANDS]
        if not weapon:
            weapon = slots[WieldLocation.WEAPON_HAND]
        # if there's still no weapon, we throw hands
        if not weapon:
            weapon = get_bare_hands()
        return weapon
    
