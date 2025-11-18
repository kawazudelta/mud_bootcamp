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

class WieldLocation(Enum):

    BACKPACK = "backpack"
    WEAPON_HAND = "weapon_hand"
    SHIELD_HAND = "shield_hand"
    TWO_HANDS = "two_handed_weapons"
    BODY = "body"   # for armor
    HEAD = "head"   # for helmets
    
class ObjType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    HELMET = "helmet"
    CONSUMABLE = "consumable"
    GEAR = "gear"
    MAGIC = "magic"
    QUEST = "quest"
    TREASURE = "treasure"

