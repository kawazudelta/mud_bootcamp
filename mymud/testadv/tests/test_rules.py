from unittest.mock import MagicMock, call, patch

#from anything import Something
from parameterized import parameterized

from evennia.utils.test_resources import BaseEvenniaTest

from .. import enums, rules
#from .. import characters, equipment, random_tables
#from .mixins import EvAdventureMixin

class TestAdvRollEngine(BaseEvenniaTest):

    def setUp(self):
        # Called before every test method
        super().setUp()
        self.roll_engine = rules.TestAdvRollEngine()

    @patch("testadv.rules.randint")
    # testing our d100 roller, should be simple enough
    def test_roll_d100(self, mock_randint):
        mock_randint.return_value = 50
        self.assertEqual(self.roll_engine.roll_d100(), 50)

    def test_is_double(self):
        # test doubles
        self.assertTrue(self.roll_engine.is_double(11))
        self.assertTrue(self.roll_engine.is_double(22))
        self.assertTrue(self.roll_engine.is_double(66))

        # test non-doubles
        self.assertFalse(self.roll_engine.is_double(10))
        self.assertFalse(self.roll_engine.is_double(12))
        self.assertFalse(self.roll_engine.is_double(59))

        # test cases outside range
        self.assertFalse(self.roll_engine.is_double(0))
        self.assertFalse(self.roll_engine.is_double(100))
        self.assertFalse(self.roll_engine.is_double(-1))

    def test_is_critical(self):
        # test for "critical success"
        self.assertEqual(self.roll_engine.is_critical(5), "critical_success")
        self.assertEqual(self.roll_engine.is_critical(1), "critical_success")
        
        # test for "critical failure"
        self.assertEqual(self.roll_engine.is_critical(96), "critical_failure")
        self.assertEqual(self.roll_engine.is_critical(100), "critical_failure")

        # test cases returning None
        self.assertIsNone(self.roll_engine.is_critical(6))
        self.assertIsNone(self.roll_engine.is_critical(95))
        self.assertIsNone(self.roll_engine.is_critical(-1))
        self.assertIsNone(self.roll_engine.is_critical(101))
        
    @patch("testadv.rules.randint")
    # tests the roll() method
    def test_roll(self, mock_randint):
        mock_randint.return_value = 4
        self.assertEqual(self.roll_engine.roll("1d6"), 4)
        self.assertEqual(self.roll_engine.roll("2d6"), 2 * 4)
        self.assertEqual(self.roll_engine.roll("1d20"), 4)

    @patch("testadv.rules.randint")
    # tests the roll_with_advantage_or_disadvantage() method
    def test_roll_with_advantage_or_disadvantage(self, mock_randint):
        mock_randint.return_value = 50

        # test without advantage or disadvantage
        self.assertEqual(self.roll_engine.roll_with_advantage_or_disadvantage(), 50)
        mock_randint.assert_called_once()
        mock_randint.reset_mock()

        # test that advantage and disadvantage cancel each other out
        self.assertEqual(self.roll_engine.roll_with_advantage_or_disadvantage(
            advantage=True, disadvantage=True), 50)
        mock_randint.assert_called_once()
        mock_randint.reset_mock()

        # run with advantage/disadvantage using rolls of 80 and 20
        mock_randint.side_effect = [80, 20]
        result = self.roll_engine.roll_with_advantage_or_disadvantage(advantage=True)
        # advantage should return the lower value, 20
        self.assertEqual(result, 20)
        # and it should have been called twice
        self.assertEqual(mock_randint.call_count, 2)
        mock_randint.reset_mock()

        mock_randint.side_effect = [80, 20]
        result = self.roll_engine.roll_with_advantage_or_disadvantage(disadvantage=True)
        # disadvantage should return the higher value, 80
        self.assertEqual(result, 80)
        # and it should have been called twice
        self.assertEqual(mock_randint.call_count, 2)

    @patch("testadv.rules.randint")
    # tests the saving_throw() method
    def test_saving_throw(self, mock_randint):
        # Set the test roll to a value that will pass PHYS checks and fail COOR checks
        mock_randint.return_value = 50

        # meet our lab rat
        character = MagicMock()
        # ooh so strong
        character.physique = 15
        # bit of a klutz, though
        character.coordination = 8

        # character should pass Phys save, no crit
        # send it over to the tested method
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS)
        # charater should pass
        self.assertTrue(success)
        # no crit success or failure
        self.assertIsNone(quality)

        # Now character should fail a Coor save, with no crit
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.COOR)
        # have a nice trip
        self.assertFalse(success)
        # see you next fall
        self.assertIsNone(quality)

        # test critical success
        # we have to start clearing the randint from this point on
        mock_randint.reset_mock()
        # set the test roll to something that should be a critical success
        mock_randint.return_value = 5
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS)
        self.assertTrue(success)
        self.assertEqual(quality, "critical_success")

        # test critical failure
        mock_randint.reset_mock()
        mock_randint.return_value = 96
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.COOR)
        self.assertFalse(success)
        self.assertEqual(quality, "critical_failure")

        # Test boundary values next
        # target is 75, so a tied roll should count as a success
        mock_randint.reset_mock()
        mock_randint.return_value = 75
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS)
        self.assertTrue(success)
        self.assertIsNone(quality)

        # Phys save fails on a 76
        mock_randint.reset_mock()
        mock_randint.return_value = 76
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS)
        self.assertFalse(success)
        self.assertIsNone(quality)

        # Coor save succeeds on a 40...
        mock_randint.reset_mock()
        mock_randint.return_value = 40
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.COOR)
        self.assertTrue(success)
        self.assertIsNone(quality)

        # ... but Coor save fails on a 41
        mock_randint.reset_mock()
        mock_randint.return_value = 41
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.COOR)
        self.assertFalse(success)
        self.assertIsNone(quality)

        # Testing Saving throws with advantage/disadvantage
        # Here, Advantage on the roll should turn a failure (80) into a success (20)
        mock_randint.reset_mock()
        # use side effect to store two rolls that we can use for test
        mock_randint.side_effect = [80, 20]
        # same call as before, but with advantage
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, advantage=True)
        self.assertTrue(success)
        self.assertIsNone(quality)
        # and we called mock_randint twice
        self.assertEqual(mock_randint.call_count, 2)

        # Rolling with advantage results in duplicate success
        mock_randint.reset_mock()
        mock_randint.side_effect = [20, 30]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, advantage=True)
        self.assertTrue(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # Our advantage turns a normal success into a crit!
        mock_randint.reset_mock()
        mock_randint.side_effect = [20, 3]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, advantage=True)
        self.assertTrue(success)
        self.assertEqual(quality, "critical_success")
        self.assertEqual(mock_randint.call_count, 2)

        # Advantage turns a critical failure into a normal success
        mock_randint.reset_mock()
        mock_randint.side_effect = [99, 30]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, advantage=True)
        self.assertTrue(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # Disadvantage turns success to failure
        mock_randint.reset_mock()
        mock_randint.side_effect = [20, 80]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, disadvantage=True)
        self.assertFalse(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # Disadvantage duplicates failures
        mock_randint.reset_mock()
        mock_randint.side_effect = [90, 80]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, disadvantage=True)
        self.assertFalse(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # Disadvantage turns a normal failure into a critical failure 
        mock_randint.reset_mock()
        mock_randint.side_effect = [80, 99]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, disadvantage=True)
        self.assertFalse(success)
        self.assertEqual(quality, "critical_failure")
        self.assertEqual(mock_randint.call_count, 2)

        # Disadvantage turns a critical success into a normal failure ;_;
        mock_randint.reset_mock()
        mock_randint.side_effect = [3, 80]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, disadvantage=True)
        self.assertFalse(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

    @patch("testadv.rules.randint")
    # tests the opposed_saving_throw() method
    def test_opposed_saving_throw(self, mock_randint):
        # test the opposed_saving_throw() method
        
        # first we mock-up our attacker 
        # target number is 60
        attacker = MagicMock()
        attacker.physique = 12 
        
        # then we mock up our defender 
        # target number is 50
        defender = MagicMock()
        defender.armor = 10 
        
        # Attacker succeeds, defender fails
        # Set the attacker, defender rolls
        mock_randint.side_effect = [40, 70]
        # call the tested method
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        # attacker should succeed...
        self.assertTrue(success)
        # ...but not critically
        self.assertIsNone(quality)
        # and we called mock_randint twice
        self.assertEqual(mock_randint.call_count, 2)

        # Attacker fails, Defender succeeds
        mock_randint.reset_mock()
        mock_randint.side_effect = [80, 30]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # Attacker and Defender both succeed, attacker wins tiebreaker
        mock_randint.reset_mock()
        # lower roll wins matched successes
        mock_randint.side_effect = [30, 40]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertTrue(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # both succeed, defender wins the tie
        mock_randint.reset_mock()
        mock_randint.side_effect = [40, 30]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # both fail, attacker wins the tiebreaker
        mock_randint.reset_mock()
        # on matched failures, the lower roll wins
        mock_randint.side_effect = [70, 80]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertTrue(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # both fail, defender wins tiebreaker
        mock_randint.reset_mock()
        mock_randint.side_effect = [80, 70]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # If the attacker crits (rolls a critical success), it takes priority over any other result
        # First check attacker's crit over a defender's fumble (critical failure)
        mock_randint.reset_mock()
        mock_randint.side_effect = [4, 99]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertTrue(success)
        self.assertEqual(quality, "critical_success")
        self.assertEqual(mock_randint.call_count, 2)

        # Attacker crits, defender fails
        mock_randint.reset_mock()
        mock_randint.side_effect = [4, 90]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertTrue(success)
        self.assertEqual(quality, "critical_success")
        self.assertEqual(mock_randint.call_count, 2)

        # Attacker crits, defender succeeds
        mock_randint.reset_mock()
        mock_randint.side_effect = [4, 30]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertTrue(success)
        self.assertEqual(quality, "critical_success")
        self.assertEqual(mock_randint.call_count, 2)

        # Attacker and defender both crit
        mock_randint.reset_mock()
        mock_randint.side_effect = [4, 4]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertTrue(success)
        self.assertEqual(quality, "critical_success")
        self.assertEqual(mock_randint.call_count, 2)

        # Now we check for cases where the attacker gets a critical failure
        # Attacker should lose, regardless of defender's roll

        # attacker fumbles, defender crits
        mock_randint.reset_mock()
        mock_randint.side_effect = [99, 4]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertEqual(quality, "critical_failure")
        self.assertEqual(mock_randint.call_count, 2)

        # attacker fumbles, defender succeeds
        mock_randint.reset_mock()
        mock_randint.side_effect = [99, 30]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertEqual(quality, "critical_failure")
        self.assertEqual(mock_randint.call_count, 2)

        # attacker fumbles, defender fails
        mock_randint.reset_mock()
        mock_randint.side_effect = [99, 80]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertEqual(quality, "critical_failure")
        self.assertEqual(mock_randint.call_count, 2)

        # attacker and defender both fumble
        mock_randint.reset_mock()
        mock_randint.side_effect = [99, 98]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertEqual(quality, "critical_failure")
        self.assertEqual(mock_randint.call_count, 2)

        # Now we give the defender a critical success, and check cases for the attacker
        # Defender crits, attacker succeeds
        mock_randint.reset_mock()
        mock_randint.side_effect = [30, 4]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        #Defender crit success, attacker normal failure
        mock_randint.reset_mock()
        mock_randint.side_effect = [80, 4]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertFalse(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # Now we check for remaining cases where the defender fumbles (critical failure)
        # Defender fumbles, attacker normal success
        mock_randint.reset_mock()
        mock_randint.side_effect = [30, 99]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertTrue(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)      

        # Defender fumbles, attacker normal failure
        mock_randint.reset_mock()
        mock_randint.side_effect = [80, 99]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR)
        self.assertTrue(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)      

        # Check advantage/disadvantage
        # Test to confirm an attacker's advantage can turn a loss into a win
        mock_randint.reset_mock()
        mock_randint.side_effect = [80, 30, 45]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR, attacker_advantage=True)
        self.assertTrue(success)
        self.assertIsNone(quality)
        # should be called twice for the attacker's advantage and once for the defender
        self.assertEqual(mock_randint.call_count, 3)
        
        # Test to confirm a defender's disadvantage can turn a win into a loss
        mock_randint.reset_mock()
        mock_randint.side_effect = [40, 30, 80]
        success, quality = self.roll_engine.opposed_saving_throw(
            attacker, defender,
                attack_type=enums.Ability.PHYS,
                    defense_type=enums.Ability.ARMOR, defender_disadvantage=True)
        self.assertTrue(success)
        self.assertIsNone(quality)
        # should be called once for the attacker and twice for the defender's disadvantage
        self.assertEqual(mock_randint.call_count, 3)

    @patch("testadv.rules.randint")
    # testing to make sure enemies can pass/fail a morale check    
    def test_morale_check(self, mock_randint):
        
        # Let's bring in our goblin
        defender = MagicMock()
        defender.morale = 9
        
        # defender should pass if they roll a 6 (3 + 3)
        mock_randint.side_effect = [3, 3]
        success = self.roll_engine.morale_check(defender)
        self.assertTrue(success)

        # defender should fail if they roll a 10 (5 + 5)
        mock_randint.reset_mock()
        mock_randint.side_effect = [5, 5]
        success = self.roll_engine.morale_check(defender)
        self.assertFalse(success)

    @patch("testadv.rules.randint")
    # test the healing method, on rest character regains 1d8 + 2xlevel HP
    def test_heal_from_rest(self, mock_randint):
    
        # Mock up our accident victim
        character = MagicMock()
        character.heal = MagicMock()
        character.level = 2

        # roll a 5 on a 1d8. Heal amount should be 5 + (2*2) = 9
        mock_randint.return_value = 5
        self.roll_engine.heal_from_rest(character)
        character.heal.assert_called_with(9)

    @patch("testadv.rules.randint")
    # Test that the random table method returns the expected item from a table
    def test_roll_random_table(self, mock_randint):

        mock_randint.return_value = 4   #should return "coordination"
        result = self.roll_engine.roll_random_table("1d8", rules.death_table)
        self.assertEqual(result, "coordination")

        # Let's make sure it parses both ends of a range as well
        mock_randint.reset_mock()
        mock_randint.return_value = 1
        result = self.roll_engine.roll_random_table("1d8", rules.death_table)
        self.assertEqual(result, "dead")

        mock_randint.reset_mock()
        mock_randint.return_value = 2
        result = self.roll_engine.roll_random_table("1d8", rules.death_table)
        self.assertEqual(result, "dead")       

    @patch("testadv.rules.randint")
    # test the roll_death() method
    def test_roll_death(self, mock_randint):

        # Today's lucky victim
        character = MagicMock()
        character.physique = 15
        character.heal = MagicMock()

        # TODO find out how killing the character works so we can test it properly
        # we already tested the return string above, so disable this one for now
        # we got it from the docs, though
        ''' 
        mock_randint.return_value = 1
        self.roll_engine.roll_death(character)
        character.at_death.assert_called()
        mock_randint.reset_mock()
        '''

        # Test loss of Physique on death. 
        # side_effects: 1d8 roll for ability (3=physique), 1d4 for loss (2), 1d4 for heal (3)
        mock_randint.side_effect = [3, 2, 3]
        self.roll_engine.roll_death(character)
        # make sure we lost 2 Phys
        self.assertEqual(character.physique, 13)
        # assert that we called the heal method with 3
        character.heal.assert_called_with(3)
        # and we called randint three times
        self.assertEqual(mock_randint.call_count, 3)