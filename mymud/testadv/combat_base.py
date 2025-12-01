from evennia import DefaultScript, create_script
from evennia.utils import evtable
from . import rules


class CombatFailure(RuntimeError):
    '''
    If some error happens in combat
    '''
    pass


class CombatAction:
    '''
    Parent class for all actions.
    '''
    def __init__(self, combathandler, combatant, action_dict):
        self.combathandler = combathandler
        self.combatant = combatant

        for key, val in action_dict.items():
            setattr(self, key, val)

    def msg(self, message, broadcast=True):
        '''
        Send message to others in combat.
        '''
        self.combathandler.msg(message, combatant=self.combatant, broadcast=broadcast)

    def can_use(self):
        '''
        Return false if the combatant cannot currently use this action
        '''
        return True
    
    def execute(self):
        '''
        Does the action.
        '''
        pass

    def post_execute(self):
        '''
        Called after execute() for cleanup/tallying.
        '''
        pass


class CombatActionHold(CombatAction):
    '''
    The action of no action.
    :: 
        action_dict = {
            "key": "hold"
        }
    '''

class CombatActionAttack(CombatAction):
    '''
    A regular attack, using a wielded weapon
    ::
        action-dict = {
            "key": "attack",
            "target": Character/Object
        }
    '''

    def execute(self):
        attacker = self.combatant
        weapon = attacker.weapon
        target = self.target

        if weapon.at_pre_use(attacker, target):
            weapon.use(
                attacker,
                target,
                attacker_advantage=self.combathandler.has_advantage(attacker, target),
                attacker_disadvantage=self.combathandler.has_disadvantage(attacker, target),
            )
            weapon.at_post_use(attacker, target)


class CombatActionStunt(CombatAction):
    '''
    Perform a stunt the grants a beneficiary (can be self) advantage on their next action against a 
    target. Whenever performing a stunt that would affect another negatively (giving them
    disadvantage against an ally, or granting an advantage against them, we need to make a check
    first. We don't do a check if giving an advantage to an ally or ourselves.

    action_dict = {
           "key": "stunt",
           "recipient": Character/NPC,
           "target": Character/NPC,
           "advantage": bool,  # if False, it's a disadvantage
           "stunt_type": Ability,  # what ability (like STR, DEX etc) to use to perform this stunt. 
           "defense_type": Ability, # what ability to use to defend against (negative) effects of
            this stunt.
        }
    '''
    def execute(self):
        combathandler=self.combathandler
        attacker = self.combatant
        recipient = self.recipient
        target = self.target
        txt = ""

        if recipient == target:
            # grant another entity dis/advantage against itself
            defender = recipient
        else:
            # Recipient and target are different
            # who defends determined by if we're giving advantage or disadvantage
            defender = target if self.advantage else recipient

        # trying to give adv to recipient against target. Target defends against caller.
        is_success, _, txt = rules.dice.opposed_saving_throw(
            attacker,
            defender,
            attack_type=self.stunt_type,
            defense_type=self.defense_type,
            attacker_advantage=combathandler.has_advantage(attacker, defender),
            attacker_disadvantage=combathandler.has_disadvantage(attacker, defender),
            defender_advantage=combathandler.has_advantage(defender, attacker),
            defender_disadvantage=combathandler.has_disadvantage(defender, attacker),
        )

        self.msg(f"$You() $conj(attempt) stunt on $You({defender.key}). {txt}")

        # deal with the results
        if is_success:
            if self.advantage:
                combathandler.give_advantage(recipient, target)
            else:
                combathandler.give_disadvantage(recipient, target)
            if recipient == self.combatant:
                self.msg(
                    f"$You() $conj(gain) {'advantage' if self.advantage else 'disadvantage'} "
                    f"against $You({target.key})!"
                )
            else:
                self.msg(
                    f"$You() $conj(cause) $You({recipient.key}) "
                    f"to gain {'advantage' if self.advantage else 'disadvantage'} "
                    f"against $You({target.key})!"
                )
            self.msg(
                "|yHaving succeeded, you hold back to plan your next move.|n [hold]",
                broadcast=False,
            )
        else:
            self.msg(f"$You({defender.key}) $conj(resist)! $You() $conj(fail) the stunt.")



class TestAdvCombatBaseHandler(DefaultScript):
    '''
    Handler is created when combat starts. It ticks the combat and tracks all sides of it. 
    Used for all combat.
    '''
    action_classes = {}
    fallback_action_dict = {}

    @classmethod
    def get_or_create_combathandler(cls, obj, **kwargs):
        '''
        Get or create a combat handler on an 'obj'.

        Args:
            obj (any): The Typeclassed entity to store this script on.
        Keyword Args:
            combathandler_key (str): Identifier for script. 'combathandler' by default
            **kwargs: Extra arguments to the Script, if it is created.
        '''
        if not obj:
            raise CombatFailure("Cannot start combat without a place to do it!")
        
        combathandler_key = kwargs.pop("key", "combathandler")
        combathandler = obj.ndb.combathandler
        if not combathandler or not combathandler.id:
            combathandler = obj.scripts.get(combathandler_key).first()
            if not combathandler:
                # this means we have to create it from scratch
                persistent = kwargs.pop("persistent", True)
                combathandler = create_script(
                    cls,
                    key=combathandler_key,
                    obj=obj,
                    persistent=persistent,
                    **kwargs,
                )
            obj.ndb.combathandler = combathandler
        return combathandler

    def msg(self, message, combatant=None, broadcast=True, location=None):
        '''
        Central place for sending messages to combatants. This allows for adding any combat-specific text-decoration in one place.
        
        Args:
            message (str): The message to send.
            combatant (Object): The 'You' in the message, if any.
            broadcast (bool): If 'False', combatant must be included and will be the only one to see the message. If 'True' send to everyone in the location.
            Location (Object, optional): If given, use this as the location to send broadcast messages to. If not, use 'self.obj' as that location.

        Notes:
            If 'combatant' is given, use $You/you() markup to create a message that looks different depending on who sees it. Use '$You(combatant_key)' to refer to other combatants.
        '''
        if not location:
            location = self.obj

        location_objs = location.contents

        exclude = []
        if not broadcast and combatant:
            exclude = [obj for obj in location_objs if obj is not combatant]

        location.msg_contents(
            message,
            exclude=exclude,
            from_obj=combatant,
            mapping={locobj.key: locobj for locobj in location_objs},
        )      

    def get_combat_summary(self, combatant):
        '''
        Gets a nicely formatted 'battle report of combat, from the perspective of the combatant.
        '''
        allies, enemies = self.get_sides(combatant)
        # get the number of allies and enemies
        nallies, nenemies = len(allies), len(enemies)

        # prepare colors(!) and hurt levels
        allies = [f"{ally} ({ally.hurt_level})" for ally in allies]
        enemies = [f"{enemy} ({enemy.hurt_level})" for enemy in enemies]

        # The center column with the 'vs'
        vs_column = ["" for _ in range(max(nallies, nenemies))]
        vs_column[len(vs_column) // 2] = "|wvs|n"

        # The two allies/enemies columns should be centered vertically
        # Here we're figuring out how many blank rows we need, and splitting them up
        diff = abs(nallies - nenemies)
        top_empty = diff // 2
        bot_empty = diff - top_empty
        topfill = ["" for _ in range(top_empty)]
        botfill = ["" for _ in range(bot_empty)]

        # Here we determine which side needs the empty filler lines
        if nallies >= nenemies:
            enemies = topfill + enemies + botfill
        else:
            allies = topfill + allies + botfill

        # Here we actually make the table that prints out
        return evtable.EvTable(
            table=[
                evtable.EvColumn(*allies, align="l"),
                evtable.EvColumn(*vs_column, align="c"),
                evtable.EvColumn(*enemies, align="r"),
            ],
            border=None,
            maxwidth=78,
        )

    def get_sides(self, combatant):
        '''
        Get who's still alive on the two sides of combat, as a tuple `([allies], [enemies])` from the perspective of `combatant` (who is _not_ included in the `allies` list).
        '''
        raise NotImplementedError
    
    def give_advantage(self, recipient, target):
        '''
        Give advantage to recipient against target.
        '''
        raise NotImplementedError
    
    def give_disadvantage(self, recipient, target):
        '''
        Give disadvantage to recipient against target.
        '''
        raise NotImplementedError
    
    def has_advantage(self, combatant, target):
        '''
        Check if recipient has advantage against target.
        '''
        raise NotImplementedError
    
    def has_disadvantage(self, combatant, target):
        '''
        Check if recipient has disadvantage against target.
        '''
        raise NotImplementedError
    
    def queue_action(self, combatant, action_dict):
        '''
        Queue an action for the combatant by providing action dict.
        '''
        raise NotImplementedError
    
    def execute_next_action(self, combatant):
        '''
        Execute the next action for the combatant.
        '''
        raise NotImplementedError
    
    def start_combat(self):
        '''
        Start combat.
        '''
        raise NotImplementedError
    
    def check_stop_combat(self):
        '''
        Check if combat is over and if it should stop.
        '''
        raise NotImplementedError
    
    def stop_combat(self):
        '''
        Stop combat and do cleanup.
        '''
        raise NotImplementedError