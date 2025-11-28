from evennia import DefaultCharacter, AttributeProperty, logger
from evennia.utils.utils import lazy_property

from .equipment import EquipmentHandler, EquipmentError
from .rules import dice

class LivingMixin:

    # This will make it easy for mobs to know to attack PCs
    is_pc = False

    @property
    def hurt_level(self):
        '''
        String describing how hurt the character is.
        '''
    
        percent = max(0, min(100, 100 * (self.hp / self.max_hp)))
        if 95 < percent <= 100:
            return "|gPerfect|n"
        elif 80 < percent <= 95:
            return "|gScuffed|n"
        elif 60 < percent <= 80:
            return "|yRoughed up|n"
        elif 45 < percent <= 60:
            return "|yBloodied|n"
        elif 30 < percent <= 45:
            return "|yInjured|n"
        elif 15 < percent <= 30:
            return "|rAll messed up|n"
        elif 1 < percent <= 15:
            return "|rNear death|n"
        elif percent == 0:
            return "|RCollapsed!|n"
        
    def heal(self, hp):
        '''
        Heal by a certain amount of HP
        '''
        damage = self.hp_max - self.hp
        healed = min(damage, hp)
        self.hp += healed

        self.msg(f"|gYou heal for {healed} HP.|n")

    def at_pay(self, amount):
        '''
        When paying coins, don't detract more than we have.
        ''' 
        # TODO is that really how they want this to work?
        amount = min(amount, self.coins)
        self.coins -= amount
        return amount

    def at_attacked(self, attacker, **kwargs):
        '''
        Called when character gets attacked and combat starts
        '''
        pass

    def at_damage(self, damage, attacker=None):
        '''
        Called when attacked and taking damage
        '''
        self.hp -= damage

    def at_defeat(self):
        '''
        Called when defeated. By default, this means death.
        '''
        self.at_death()

    def at_death(self):
        '''
        Called when this thing dies. This will mean different things depending on who's doing the dying.
        '''
        pass

    def do_at_loot(self, looted):
        '''
        Called when looting another entity
        '''
        looted.at_looted(self)

    def at_looted(self, looter):
        '''
        Called when looted by another entity
        '''
        # Currently defaults to stealing some coins
        max_steal = dice.roll("1d10")
        stolen = self.at_pay(max_steal)
        looter.coins += stolen


class TestAdvCharacter(LivingMixin, DefaultCharacter):
    '''
    A character to use for TestAdv.
    '''
    is_pc = True
    
    physique = AttributeProperty(1)
    coordination = AttributeProperty(1)
    instinct = AttributeProperty(1)
    reason = AttributeProperty(1)
    willpower = AttributeProperty(1)
    auspice = AttributeProperty(1)
    
    armor = AttributeProperty(11)

    hp = AttributeProperty(8)
    hp_max = AttributeProperty(8)
    
    level = AttributeProperty(1)
    xp = AttributeProperty(0)
    coins = AttributeProperty(0)

    @lazy_property  # won't load the handler until someone actually tries to fetch it
    def equipment(self):
        return EquipmentHandler(self)
    
    def at_pre_object_receive(self, moved_object, source_location, **kwargs):
        '''
        Called by Evennia before an object arrives in the character
        So, before the pick something up (inventory not full, etc.)
        If it returns False, pickup is aborted.
        '''
        return self.equipment.validate_slot_usage(moved_object)

    def at_object_receive(self, moved_object, source_location, **kwargs):
        '''
        Called by Evennia when an object arrives "in" the character
        '''
        try:
            self.equipment.add(moved_object)
        except EquipmentError:
            # this is not an equipment object, that's fine.
            pass
        except Exception:
            logger.log_trace()

    def at_object_leave(self, moved_object, destination, **kwargs):
        '''
        Called by Evennia when an object leaves the character
        '''
        self.equipment.remove(moved_object)

    def at_defeat(self):
        '''
        Characters roll on the death table.
        '''
        if self.location.allow_death:
            # This allows rooms to have non-lethal battles
            dice.roll_death(self)
        else:
            self.location.msg_contents(
                "$You() $conj(collapse) in a heap, alive but beaten.",
                from_obj=self)
            self.heal(self.hp_max)

    def at_death(self):
        '''
        We rolled 'dead' on the death table
        '''
        self.location.msg_contents(
            "$You() $conj(collapse) in a heap, embraced by death.",
            from_obj=self)
        # TODO go back to chargen to make a new character