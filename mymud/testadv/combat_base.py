from evennia import DefaultScript, create_script


class CombatFailure(RuntimeError):
    '''
    If some error happens in combat
    '''
    pass


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

    def msg(self, message, combatant=None, broadcast=True, location=True):
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
        pass    # TODO

        # Implemented differently in twitch/turnbased combat

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