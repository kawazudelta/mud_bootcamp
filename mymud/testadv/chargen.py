from .random_tables import chargen_tables
from .rules import dice

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