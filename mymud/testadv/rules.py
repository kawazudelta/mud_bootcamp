from random import randint
from .enums import Ability


class TestAdvRoleEngine:

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
            str or None: "critical_success" if the roll is 1,
                        "critical_failure" if the roll is 100,
                        None otherwise.
        """
        if roll_result == 1:
            return "critical_success"
        elif roll_result == 100:
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

    # def saving_throw(...):
    #     # do a saving throw against a specific target number?

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