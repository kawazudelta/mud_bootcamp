import random

from evennia.utils.logger import log_trace
from evennia.utils.utils import lazy_property

from .enums import Ability


class AIHandler:
    attribute_name = "ai_state"
    attribute_category = "ai_state"

    def __init__(self, obj):
        self.obj = obj
        self.ai_state = obj.attributes.get(
            self.attribute_name,
            category=self.attribute_category,
            default="idle")
        
    def set_state(self, state):
        self.ai_state = state
        self.obj.attributes.add(self.attribute_name, state, category=self.attribute_category)

    def get_state(self):
        return self.ai_state
    
    def get_targets(self):
        '''
        Get a list of potential targets for NPCs to combat
        '''
        return [obj for obj in self.obj.location.contents if hasattr(obj, "is_pc") and obj.is_pc]
    
    def get_traversable_exits(self, exclude_destination=None):
        '''
        Get (and optionally exclude) a list of exits an NPC/mob can traverse
        
        Args:
            exclude_destination (Object, optional): Exclude exits with this destination.
        '''
        return [
            exi
            for exi in self.obj.location.exits
            if exi.destination != exclude_destination and exi.access(self.obj, "traverse")
        ]
    
    def random_probability(self, probabilities):
        '''
        Given a dict of probabilities, return the key of the chosen probability.
        
        Args:
            probabilities (dict): A dictionary of probabilities, where the key is the action and the value is the probability of that action.
        '''
        prob_total = sum(probabilities.values())
        sorted_probs = sorted(
            ((key, prob / prob_total) for key, prob in probabilities.items()),
            key=lambda x: x[1],
            reverse=True,
        )
        rand = random.random()
        total = 0
        for key, prob in sorted_probs:
            total += prob
            if rand <= total:
                return key
    
    def run(self):
        try:
            state = self.get_state()
            getattr(self.obj, f"ai_{state}")()
        except Exception:
            log_trace(f"AI error in {self.obj.name} (running state: {state})")
    