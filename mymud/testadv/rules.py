from random import randint, choice
from .enums import Ability

# define the possible results of reaching 0 hp
death_table = (
    ("1-2", "dead"),
    ("3", "physique"),
    ("4", "coordination"),
    ("5", "instinct"),
    ("6", "reason"),
    ("7", "willpower"),
    ("8", "auspice"),
)

class TestAdvRollEngine:

    def roll_d100(self):
        """
        Rolls a 1d100.

        Returns:
            int: A random integer between 1 and 100.
        """
        return randint(1, 100)

    def is_double(self, roll_result):
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

    def is_critical(self, roll_result):
        """
        Checks if a d100 roll is a critical success or failure.

        Args:
            roll_result (int): The result of a d100 roll.

        Returns:
            str or None: "critical_success" if the roll is 5 or lower,
                        "critical_failure" if the roll is 96 or higher,
                        None otherwise.
        """
        if 1 <= roll_result <= 5:
            return "critical_success"
        elif 96 <= roll_result <= 100:
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
        ability_name = tested_ability.value

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

    def opposed_saving_throw(self, attacker, defender, 
                             attack_type=Ability.PHYS, defense_type=Ability.ARMOR, 
                             attacker_advantage=False, attacker_disadvantage=False,
                             defender_advantage=False, defender_disadvantage=False):
        '''
        Performs an opposed roll between an attacker and a defender.
        
        Args:
            attacker (Character): the one performing the action.
            defender (Character): The one resisting the action.
            attack_type (Ability): Ability score used by the attacker.
            defense_type (Ability): Ability score used by the defender.
            attacker_advantage (bool): if attacker has advantage on this roll.
            attacker_disadvantage (bool): if attacker has disadvantage on this roll.
            defender_advantage (bool): if defender has advantage on this roll.
            defender_disadvantage (bool): if defender has disadvantage on this roll.
        
        Returns:
            tuple: A tuple of (bool, str, str). 
            The bool is True if the attacker succeeds. 
            The first str is for any critical success/failure. 
            The second str is a descriptive string for the player
        '''

        # Attacker rolls
        attacker_score = getattr(attacker, attack_type.value.lower(), 0)
        attacker_target = attacker_score * 5
        attacker_roll = self.roll_with_advantage_or_disadvantage(attacker_advantage, attacker_disadvantage)
        attacker_success = attacker_roll <= attacker_target
        attacker_quality = self.is_critical(attacker_roll)
        
        # Defender rolls
        defender_score = getattr(defender, defense_type.value.lower(), 0)
        defender_target = defender_score * 5
        defender_roll = self.roll_with_advantage_or_disadvantage(defender_advantage, defender_disadvantage)
        defender_success = defender_roll <= defender_target
        defender_quality = self.is_critical(defender_roll)

        # Return a descriptive string
        txt = (
            f"Attack Roll ({attack_type.value}): {attacker_roll} (Target: {attacker_target}) "
            f"| Defense Roll ({defense_type.value}): {defender_roll} (Target: {defender_target})"
        )
        
        # Let's check for any crits first
        if attacker_quality == "critical_success":
            # attacker crit automatically wins ties
            return True, "critical_success", txt
        elif attacker_quality == "critical_failure":
            # if the attacker fumbles, that's that
            return False, "critical_failure", txt
        elif defender_quality == "critical_success":
            # defender scores a critical success and the attacker didn't, they just win, no tiebreakers
            return False, None, txt
        elif defender_quality == "critical_failure":
            # if the defender fumbles, and the attacker didn't, attacker wins
            return True, None, txt
        
        # At this point, nobody has scored a crit of any kind
        elif attacker_success and not defender_success:
            #attacker succeeds and defender fails, that's easy
            return True, None, txt
        elif not attacker_success and defender_success:
            # defender succeeds
            return False, None, txt
        elif attacker_success and defender_success:
            # both succeed without critting, lowest roll wins
            # This deviates from OpenQuest, but plays better with advantage/disadvantage
            # attacker wins ties
            return attacker_roll <= defender_roll, None, txt
        else: # this means both failed without fumbling, so lowest roll wins
            return attacker_roll <= defender_roll, None, txt
    
    def morale_check(self, defender):
        # roll a morale check for a target 
        return self.roll("2d6") <= getattr(defender, "morale", 9)
        
    def heal_from_rest(self, character): 
        """ 
        A night's rest retains 1d8 + 2xlevel HP  
        
        """
        level = getattr(character, "level", 1)
        heal_bonus = level * 2
        character.heal(self.roll("1d8") + heal_bonus)

    def roll_random_table(self, dieroll, table_choices):
        '''
        Args:
            dieroll (str): a die roll string, like "1d20"
            table_choices (iterable): A list of either single elements or of tuples
        Returns:
            Any: A random result from the given list of choices

        Raises:
            RuntimeError: If rolling dice gives results outside the table
        '''
        roll_result = self.roll(dieroll)
        
        if isinstance(table_choices[0], (tuple, list)):
            # if the first element is a tuple/list; treat as on the form [("1-5", "item"),...]
            for (valrange, choice) in table_choices:
                minval, *maxval = valrange.split("-", 1)
                minval = abs(int(minval))
                maxval = abs(int(maxval[0]) if maxval else minval)

                if minval <= roll_result <= maxval:
                    return choice

            # for dierolls producing values outside the table...    
            # if we got here we beansed it, team. 
            raise RuntimeError("roll_random_table: Invalid die roll")
        else:
            # a simple, regular list
            roll_result = max(1, min(len(table_choices), roll_result))
            return table_choices[roll_result - 1]
            
    def roll_death(self, character):
        #roll to determine penalty when hitting 0 HP.
        ability_name = self.roll_random_table("1d8", death_table)
        
        if ability_name == "dead":
            # kill the character
            character.at_death()
        else:
            loss = self.roll("1d4")

            current_ability = getattr(character, ability_name)
            current_ability -= loss

            if current_ability <= 0:
                # kill the character
                character.at_death()
            else:
                # refresh 1d4 health but suffer 1d4 ability loss
                character.heal(self.roll("1d4"))
                setattr(character, ability_name, current_ability)

                character.msg(
                    "You survive your brush with death, and while you recover "
                    f"some health, you permanently lose {loss} {ability_name} instead."
                )
       
dice = TestAdvRollEngine()