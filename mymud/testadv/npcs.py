import random

from evennia import DefaultCharacter, AttributeProperty
from evennia.utils.utils import lazy_property

from .ai import AIHandler
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
    @lazy_property
    def ai(self): 
        return AIHandler(self)

    @property
    def combat_probabilities(self):
        return {
            "attack": 0.7,
            "stunt": 0.1,
            "item": 0.1,
            "flee": 0.1
        }

    def ai_idle(self): 
        pass 

    def ai_roam(self):
        '''
        roam, moving randomly to a new room. If a target is found, switch to combat state.
        '''
        if targets := self.ai.get_targets():
            self.ai.set_state("combat")
            self.execute_cmd(f"attack {random.choice(targets).key}")
        else:
            exits = self.ai.get_traversable_exits()
            if exits:
                exi = random.choice(exits)
                self.execute_cmd(f"{exi.key}") 

    def ai_combat(self): 
        '''
        Manage the combat/combat state of the mob.

        '''
        if combathandler := self.ndb.combathandler:
            # already in combat
            allies, enemies = combathandler.get_sides(self)
            action = self.ai.random_probability(self.combat_probabilities)

            match action:
                case "hold":
                    combathandler.queue_action({"key": "hold"})
                case "attack":
                    combathandler.queue_action({"key": "attack", "target": random.choice(enemies)})
                case "stunt":
                    # choose a random ally to help
                    combathandler.queue_action(
                        {
                            "key": "stunt",
                            "recipient": random.choice(allies),
                            "advantage": True,
                            "stunt_type": Ability.PHYS,
                            "defense_type": Ability.COOR,
                        }
                    )
                case "item":
                    # use a random item on a random ally
                    target = random.choice(allies)
                    valid_items = [item for item in self.contents if item.at_pre_use(self, target)]
                    combathandler.queue_action(
                        {"key": "item", "item": random.choice(valid_items), "target": target}
                    )
                case "flee":
                    self.ai.set_state("flee")

        elif not (targets := self.ai.get_targets()):
            self.ai.set_state("roam")
        else:
            target = random.choice(targets)
            self.execute_cmd(f"attack {target.key}") 

    def ai_flee(self):
        '''
        Flee from the current room, avoiding going back to the room from which we came. If no exits
        are found, switch to roam state.

        '''
        current_room = self.location
        past_room = self.attributes.get("past_room", category="ai_state", default=None)
        exits = self.ai.get_traversable_exits(exclude_destination=past_room)
        if exits:
            self.attributes.add("past_room", current_room, category="ai_state")
            exi = random.choice(exits)
            self.execute_cmd(f"{exi.key}")
        else:
            # if in a dead end, roam will allow for backing out
            self.ai.set_state("roam")    




