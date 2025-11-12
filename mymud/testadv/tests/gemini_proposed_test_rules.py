import unittest
from unittest.mock import patch
from ..rules import TestAdvRollEngine, dice
from ..enums import Ability

class MockCharacter:
    def __init__(self, phys=0, armor=0):
        self.phys = phys
        self.armor = armor

class TestOpposedSavingThrow(unittest.TestCase):
    def setUp(self):
        self.roll_engine = TestAdvRollEngine()
        self.attacker = MockCharacter(phys=50)
        self.defender = MockCharacter(armor=50)

    @patch('testadv.rules.TestAdvRollEngine.roll_with_advantage_or_disadvantage')
    def test_attacker_success_defender_fail(self, mock_roll):
        # Attacker rolls 25 (success vs target of 250), defender rolls 75 (fail vs target of 250)
        mock_roll.side_effect = [25, 75]
        
        result, quality = self.roll_engine.opposed_saving_throw(
            self.attacker, self.defender,
            attack_type=Ability.PHYS,
            defense_type=Ability.ARMOR
        )
        
        self.assertTrue(result)
        self.assertIsNone(quality)

    @patch('testadv.rules.TestAdvRollEngine.roll_with_advantage_or_disadvantage')
    def test_attacker_fail_defender_success(self, mock_roll):
        # Attacker rolls 75 (fail), defender rolls 25 (success)
        mock_roll.side_effect = [75, 25]
        
        result, quality = self.roll_engine.opposed_saving_throw(
            self.attacker, self.defender,
            attack_type=Ability.PHYS,
            defense_type=Ability.ARMOR
        )
        
        self.assertFalse(result)
        self.assertIsNone(quality)

    @patch('testadv.rules.TestAdvRollEngine.roll_with_advantage_or_disadvantage')
    def test_both_succeed_attacker_wins_tie(self, mock_roll):
        # Both succeed, attacker rolls higher (25) than defender (20)
        mock_roll.side_effect = [25, 20]
        
        result, quality = self.roll_engine.opposed_saving_throw(
            self.attacker, self.defender,
            attack_type=Ability.PHYS,
            defense_type=Ability.ARMOR
        )
        
        self.assertTrue(result)
        self.assertIsNone(quality)

    @patch('testadv.rules.TestAdvRollEngine.roll_with_advantage_or_disadvantage')
    def test_both_fail_attacker_wins_tie(self, mock_roll):
        # Both fail, attacker rolls lower (75) than defender (80)
        mock_roll.side_effect = [75, 80]
        
        result, quality = self.roll_engine.opposed_saving_throw(
            self.attacker, self.defender,
            attack_type=Ability.PHYS,
            defense_type=Ability.ARMOR
        )
        
        self.assertTrue(result)
        self.assertIsNone(quality)

    @patch('testadv.rules.TestAdvRollEngine.roll_with_advantage_or_disadvantage')
    def test_attacker_critical_success(self, mock_roll):
        # Attacker rolls a critical success (5)
        mock_roll.side_effect = [5, 50]
        
        result, quality = self.roll_engine.opposed_saving_throw(
            self.attacker, self.defender,
            attack_type=Ability.PHYS,
            defense_type=Ability.ARMOR
        )
        
        self.assertTrue(result)
        self.assertEqual(quality, "critical_success")

    @patch('testadv.rules.TestAdvRollEngine.roll_with_advantage_or_disadvantage')
    def test_defender_critical_success(self, mock_roll):
        # Defender rolls a critical success (5)
        mock_roll.side_effect = [50, 5]
        
        result, quality = self.roll_engine.opposed_saving_throw(
            self.attacker, self.defender,
            attack_type=Ability.PHYS,
            defense_type=Ability.ARMOR
        )
        
        self.assertFalse(result)
        self.assertIsNone(quality)

    @patch('testadv.rules.TestAdvRollEngine.roll_with_advantage_or_disadvantage')
    def test_attacker_critical_failure(self, mock_roll):
        # Attacker rolls a critical failure (96)
        mock_roll.side_effect = [96, 50]
        
        result, quality = self.roll_engine.opposed_saving_throw(
            self.attacker, self.defender,
            attack_type=Ability.PHYS,
            defense_type=Ability.ARMOR
        )
        
        self.assertFalse(result)
        self.assertEqual(quality, "critical_failure")

    @patch('testadv.rules.TestAdvRollEngine.roll_with_advantage_or_disadvantage')
    def test_defender_critical_failure(self, mock_roll):
        # Defender rolls a critical failure (96)
        mock_roll.side_effect = [50, 96]
        
        result, quality = self.roll_engine.opposed_saving_throw(
            self.attacker, self.defender,
            attack_type=Ability.PHYS,
            defense_type=Ability.ARMOR
        )
        
        self.assertTrue(result)
        self.assertIsNone(quality)

if __name__ == '__main__':
    unittest.main()
