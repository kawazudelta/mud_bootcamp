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
        mock_randint.return_value = 50

        character = MagicMock()
        character.physique = 15
        character.coordination = 8

        # Expect character to succeed phys save and fail coor save
        # pass Phys save, no crit
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS)
        self.assertTrue(success)
        self.assertIsNone(quality)

        # fail Coor save, no crit
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.COOR)
        self.assertFalse(success)
        self.assertIsNone(quality)

        # test critical success
        mock_randint.reset_mock()
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

        # Boundary test
        # Phys succeeds on 75
        mock_randint.reset_mock()
        mock_randint.return_value = 75
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS)
        self.assertTrue(success)
        self.assertIsNone(quality)

        # Phys fails on 76
        mock_randint.reset_mock()
        mock_randint.return_value = 76
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS)
        self.assertFalse(success)
        self.assertIsNone(quality)

        # Coor succeeds on 40
        mock_randint.reset_mock()
        mock_randint.return_value = 40
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.COOR)
        self.assertTrue(success)
        self.assertIsNone(quality)

        # Coor fails on 41
        mock_randint.reset_mock()
        mock_randint.return_value = 41
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.COOR)
        self.assertFalse(success)
        self.assertIsNone(quality)

        # Testing Saving throws with advantage/disadvantage
        # Advantage turns failure to success
        mock_randint.reset_mock()
        mock_randint.side_effect = [80, 20]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, advantage=True)
        self.assertTrue(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # Advantage duplicates success
        mock_randint.reset_mock()
        mock_randint.side_effect = [20, 30]
        success, quality = self.roll_engine.saving_throw(character, tested_ability=enums.Ability.PHYS, advantage=True)
        self.assertTrue(success)
        self.assertIsNone(quality)
        self.assertEqual(mock_randint.call_count, 2)

        # Advantage turns a success into a crit!
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

    def test_opposed_saving_throw(self, mock_randint):

    # def test_morale_check(self, mock_randint):    

    # def test_heal_from_rest(self, mock_randint):

    # def test_roll_random_table(self, mock_randint):

    # def roll_death(self, mock_randint):