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

    ARMOR = "armor"

    CRITICAL_FAILURE = "fumble"
    CRITICAL_SUCCESS = "crit"
    FAILURE = "failure"
    SUCCESS = "success"

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