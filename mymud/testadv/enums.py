from enum import Enum

class Ability(Enum):
    '''
    The six base ability scores
    '''
    PHYS = "physique"
    COOR = "coordination"
    INST = "instinct"
    REAS = "reason"
    WILL = "willpower"
    AUSP = "auspice"

    ARMOR = "Armor"

    CRITICAL_FAILURE = "Critical Failure"
    CRITICAL_SUCCESS = "Critical Success"
    FAILURE = "Failure"
    SUCCESS = "Success"

    ALLEGIANCE_HOSTILE = "hostile"
    ALLEGIANCE_NEUTRAL = "neutral"
    ALLEGIANCE_FRIENDLY = "friendly"


ABILITY_REVERSE_MAP =  {
    "phys": Ability.PHYS,
    "coor": Ability.COOR,
    "inst": Ability.INST,
    "reas": Ability.REAS,
    "will": Ability.WILL,
    "ausp": Ability.AUSP,
}