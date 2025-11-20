from .enums import WieldLocation, Ability

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
        First check if they can quip it at all
        '''
        if not inherits_from(obj, TestAdvObject):
            # in case we mis with non TestAdv objects
            raise EquipmentError(f"{obj.key} isn't equippable.")
        
        size = obj.size
        max_slots = self.max_slots
        current_slot_usage = self.count_slots()
        return current_slot_usage + size <= max_slots