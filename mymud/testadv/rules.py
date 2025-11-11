from random import randint
from .enums import Ability


class TestAdvRollEngine:

    def roll_d100():
        """
        Rolls a 1d100.

        Returns:
            int: A random integer between 1 and 100.
        """
        return randint(1, 100)

    def is_double(roll_result):
        """
        Checks if a given d100 roll result is a double (11, 22, etc.).

        Args:
            roll_result (int): The result of a die roll to check.

        Returns:
            bool: True if the roll is a double, False otherwise.
        """
        # A roll is a "double" if it's a multiple of 11.
        # We also ensure the number is between 1-99 for this rule.
        return (roll_result > 0) and (roll_result < 100) and (roll_result % 11 == 0)

    def is_critical(roll_result):
        """
        Checks if a d100 roll is a critical success or failure.

        Args:
            roll_result (int): The result of a d100 roll.

        Returns:
            str or None: "critical_success" if the roll is 5 or lower,
                        "critical_failure" if the roll is 96 or higher,
                        None otherwise.
        """
        if roll_result <= 5:
            return "critical_success"
        elif roll_result >= 96:
            return "critical_failure"
        else:
            return None
        
    def roll(self, roll_string):
        '''
        Roll XdY dice, where X is the number of dice and Y is the die type.

        Args:
            roll_string (str): a dice string on the form XdY.
        Returns:
            int: The result of the roll.
        '''
        
        # split the XdY input on the 'd' one time (lol)
        number, diesize = roll_string.split("d", 1)

        # convert from string to integer
        number = int(number)
        diesize = int(diesize)

        # make the roll
        return sum(randint(1, diesize) for _ in range(number))

    def roll_with_advantage_or_disadvantage(self, advantage=False, disadvantage=False):
        # we're using d100 roll UNDER, so advantage gives us the lowest of 2, disadvantage gives us the highest

        if not (advantage or disadvantage) or (advantage and disadvantage):
            # no advantage/disadvantage or they cancel each other out
            return self.roll_d100()
        elif advantage:
            # lowest of 2 d100 rolls
            return min(self.roll_d100(), self.roll_d100())
        else:
            # highest of 2 d100 rolls
            return max(self.roll_d100(), self.roll_d100())

    def saving_throw(self, character, tested_ability=Ability.PHYS, advantage=False, disadvantage=False):
        '''
        Modification of the saving throw rules, Saving throws are rolled on a d100 against a target that is 5 times the targeted attribute.
        
        Args:
            character (Character): A character (assumed to have Ability bonuses stored on itself as Attributes).
            tested_ability (Ability): A valid Ability score enum.
            advantage (bool): if character has advantage on this roll.
            disadvantage (bool): if character has disadvantage on this roll.
        
        Returns:
            tuple: A tuple (bool, str or None), showing if the throw succeeded, and the quality is one of None or Ability.CRITICAL_FAILURE/SUCCESS
        '''

        # Get the ability's name and lowercase it
        ability_name = tested_ability.name.lower()

        # Get the actual score from the character sheet
        ability_score = getattr(character, ability_name, 0)

        # Calculate the target using the score we just pulled
        target = ability_score * 5

        # roll 1d100
        dice_roll = self.roll_with_advantage_or_disadvantage(advantage, disadvantage)

        # figure out if we had a critical success/failure
        quality = self.is_critical(dice_roll)

        # return a tuple
        return dice_roll <= target, quality

    # def opposed_saving_throw(...):
    #     # do an opposed saving throw against a target's defense

    # def roll_random_table(...):
    #     # roll on a random table (loaded elsewhere)
    
    # def morale_check(...):
    #     # roll a morale check for a target

    # def heal_from_rest(...):
    #     #heal 1d8 when resting+eating, but not more than max HP.

    # def roll_death(...):
    #     #roll to determine penalty when hitting 0 HP.

dice = TestAdvRollEngine()