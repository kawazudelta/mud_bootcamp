import random

class TestAdvRoleEngine:

    def roll_d100():
        """
        Rolls a 1d100.

        Returns:
            int: A random integer between 1 and 100.
        """
        return random.randint(1, 100)

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
        
