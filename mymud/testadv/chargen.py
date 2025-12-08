from .characters import TestAdvCharacter
from .random_tables import chargen_tables
from .rules import dice

from evennia import create_object, EvMenu
from evennia.prototypes.spawner import spawn

_ABILITIES = {
    "PHYS": "physique",
    "COOR": "coordination",
    "INST": "instinct",
    "REAS": "reason",
    "WILL": "willpower",
    "AUSP": "auspice",
}

_TEMP_SHEET = """
{name}

PHYS: {physique}
COOR: {coordination}
INST: {instinct}
REAS: {reason}
WILL: {willpower}
AUSP: {auspice}

{description}

Your belongings:
{equipment}
"""

class TemporaryCharacterSheet:

    def _random_ability(self):
        #making a change from the source material here, we're showing whole stats, and setting the floor at 7
        return max(7, dice.roll("3d6"))
    
    def __init__(self):
        self.ability_changes = 0 # how many times we've swapped ability scores during chargen

        # roll for a random name, you mutt
        self.name = dice.roll_random_table("1d282", chargen_tables["name"])

        # roll base ability scores
        self.physique = self._random_ability()
        self.coordination = self._random_ability()
        self.instinct = self._random_ability()
        self.reason = self._random_ability()
        self.willpower = self._random_ability()
        self.auspice = self._random_ability()

        # roll random physical attributes you donkey, you absolute pig
        bodytype = dice.roll_random_table("1d20", chargen_tables["body type"])
        face = dice.roll_random_table("1d20", chargen_tables["face"])
        skin = dice.roll_random_table("1d20", chargen_tables["skin"])
        hair = dice.roll_random_table("1d20", chargen_tables["hair"])
        clothing = dice.roll_random_table("1d20", chargen_tables["clothing"])
        speech = dice.roll_random_table("1d20", chargen_tables["speech"])
        virtue = dice.roll_random_table("1d20", chargen_tables["virtue"])
        vice = dice.roll_random_table("1d20", chargen_tables["vice"])
        background = dice.roll_random_table("1d20", chargen_tables["background"])
        misfortune = dice.roll_random_table("1d20", chargen_tables["misfortune"])
        alignment = dice.roll_random_table("1d20", chargen_tables["alignment"])

        self.desc = (
            f"You are {bodytype} with a {face} face, {skin} skin, {hair} hair, {speech} speech,"
            f" and {clothing} clothing. You were a {background.title()}, but you were"
            f" {misfortune} and ended up a knave. You are {virtue} but also {vice}. You are of the"
            f" {alignment} alignment."
        )

        # set starting hp, level, xp
        self.hp_max = max(5, dice.roll("1d8"))
        self.hp = self.hp_max
        self.xp = 0
        self.level = 1

        # random equipment
        self.armor = dice.roll_random_table("1d20", chargen_tables["armor"])

        _helmet_and_shield = dice.roll_random_table("1d20", chargen_tables["helmets and shields"])
        self.helmet = "helmet" if "helmet" in _helmet_and_shield else "none"
        self.shield = "shield" if "shield" in _helmet_and_shield else "none"

        self.weapon = dice.roll_random_table("1d20", chargen_tables["starting weapon"])

        self.backpack = [
            "ration",
            "ration",
            dice.roll_random_table("1d20", chargen_tables["dungeoning gear"]),
            dice.roll_random_table("1d20", chargen_tables["dungeoning gear"]),
            dice.roll_random_table("1d20", chargen_tables["general gear 1"]),
            dice.roll_random_table("1d20", chargen_tables["general gear 2"]),
        ]

    def show_sheet(self):
        # first we need to build a string that lists the equipment
        equipment = (
            str(item)
            for item in [self.armor, self.helmet, self.shield, self.weapon] + self.backpack
            if item    
        )

        # format the values to plug into the display string
        return _TEMP_SHEET.format(
            name=self.name,
            physique=self.physique,
            coordination=self.coordination,
            instinct=self.instinct,
            reason=self.reason,
            willpower=self.willpower,
            auspice=self.auspice,
            description=self.desc,
            equipment=", ".join(equipment),        
        )
    
    def apply(self):
        # create a character object with given abilities
        new_character = create_object(
            TestAdvCharacter,
            key=self.name,
            attributes=(
                ("physique", self.physique),
                ("coordination", self.coordination),
                ("instinct", self.instinct),
                ("reason", self.reason),
                ("willpower", self.willpower),
                ("auspice", self.auspice),
                ("hp", self.hp),
                ("hp_max", self.hp_max),
                ("desc", self.desc),
            ),
        )

        # spawn random starting equipment
        if self.weapon:
            weapon = spawn(self.weapon)
            if weapon:
                 new_character.equipment.move(weapon[0])
        
        if self.shield and self.shield != "none":
            shield = spawn(self.shield)
            if shield:
                 new_character.equipment.move(shield[0])

        if self.helmet and self.helmet != "none":
            helmet = spawn(self.helmet)
            if helmet:
                 new_character.equipment.move(helmet[0])

        if self.armor and "no" not in self.armor:
            armor = spawn(self.armor)
            if armor:
                 new_character.equipment.move(armor[0])
        
        for item in self.backpack:
            # these items are just in the backpack
            item_obj = spawn(item)
            if item_obj:
                 # moving to the character will automatically add to backpack
                 # via the at_object_receive hook
                 item_obj[0].move_to(new_character, quiet=True)
        
        return new_character
    

# Chargen Menu
def node_chargen(caller, raw_string, **kwargs):

    tmp_character = kwargs["tmp_character"]

    text = tmp_character.show_sheet()

    options = [
        {
            "desc": "Change your name",
            "goto": ("node_name_change", kwargs)
        }
    ]

    if tmp_character.ability_changes <= 0:
        options.append(
            {
                "desc": "Swap two of your ability scores (once)",
                "goto": ("node_swap_abilities", kwargs),
            }
        )
    
    options.append(
        {
            "desc": "Accept and create character",
            "goto": ("node_apply_character", kwargs),
        }
    )

    return text, options


def _update_name(caller, raw_string, **kwargs):
    '''
    Used by node_name_change to check what user entered and update the name if appropriate
    '''
    if raw_string:
        tmp_character = kwargs["tmp_character"]
        tmp_character.name = raw_string.lower().capitalize()

    return "node_chargen", kwargs


def node_name_change(caller, raw_string, **kwargs):
    '''
    Change the random name of the character
    '''
    tmp_character = kwargs["tmp_character"]

    text = (
        f"Your current name is |w{tmp_character.name}|n. "
        "Enter a new name or leave empty to abort."
    )

    options = {"key": "_default", "goto": (_update_name, kwargs)}
    
    return text, options


def _swap_abilities(caller, raw_string, **kwargs):        
    '''
    Used by node_swap_abilities to parse the uders input and swap ability values
    '''
    
    if raw_string:
        abi1, *abi2 = raw_string.split(" ", 1)
        # check for issues with the raw string from the user first
        if not abi2:
            caller.msg("That doesn't look right...")
            return None, kwargs
        abi2 = abi2[0]
        abi1, abi2 = abi1.upper().strip(), abi2.upper().strip()
        if abi1 not in _ABILITIES or abi2 not in _ABILITIES:
            caller.msg("Not a familiar set of abilities...")
            return None, kwargs
        # otherwise, if the input looks readable we swap values
        tmp_character = kwargs["tmp_character"]
        abi1 = _ABILITIES[abi1]
        abi2 = _ABILITIES[abi2]
        abival1 = getattr(tmp_character, abi1)
        abival2 = getattr(tmp_character, abi2)

        setattr(tmp_character, abi1, abival2)
        setattr(tmp_character, abi2, abival1)
        tmp_character.ability_changes += 1

    return "node_chargen", kwargs


def node_swap_abilities(caller, raw_string, **kwargs):
    '''
    You can swap 2 ability scores, once
    '''
    tmp_character = kwargs["tmp_character"]

    text = f"""
Your current abilities:

PHYS: {tmp_character.physique}
COOR: {tmp_character.coordination}
INST: {tmp_character.instinct}
REAS: {tmp_character.reason}
WILL: {tmp_character.willpower}
AUSP: {tmp_character.auspice}

You can swap the values of two abilities.
You can only do this once!

To swap the values of PHYS and WILL, for example, write |wPHYS WILL|n. Empty to abort.
"""

    options = {"key": "_default", "goto": (_swap_abilities, kwargs)}

    return text, options


def node_apply_character(caller, raw_string, **kwargs):
    '''
    End chargen and create the character. And puppet it.
    '''
    tmp_character = kwargs["tmp_character"]
    new_character = tmp_character.apply()

    # Link to account
    caller.characters.add(new_character)
    
    # Add puppet lock so the account can control it
    new_character.locks.add(f"puppet:id({caller.id}) or pid({caller.id}) or perm(Developer) or pperm(Developer)")

    # Auto-puppet the character
    # We try to get the session from the caller (Account)
    session = caller.sessions.get()[0] if caller.sessions.count() else None
    if session:
        caller.puppet_object(session, new_character)

    text = f"Character '{new_character.key}' created! You are now entering the game."

    # returning None instead of options means we exit the menu
    return text, None


def start_chargen(caller, session=None):
    '''
    This is a start point for spinning up the chargen from a command later
    '''
    # menutree contains all the nodes in the chargen menu tree
    menutree = {
        "node_chargen": node_chargen,
        "node_name_change": node_name_change,
        "node_swap_abilities": node_swap_abilities,
        "node_apply_character": node_apply_character,
    } 

    # this generates all random components of the character
    tmp_character = TemporaryCharacterSheet()

    EvMenu(
        caller,
        menutree,
        session=session,
        startnode="node_chargen",
        startnode_input=("", {"tmp_character": tmp_character}),
    )