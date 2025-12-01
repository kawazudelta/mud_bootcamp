"""
Tests for the combat system.
"""

from unittest.mock import MagicMock, patch
from evennia import create_object
from evennia.utils.test_resources import EvenniaTestCase
from .. import combat_base
from .. import rules 
from .. import objects 

class TestCombatHandlerBase(EvenniaTestCase):
    """
    Test the base combat handler.
    """
    
    def setUp(self):
        super().setUp()
        self.char1 = create_object("evennia.objects.objects.DefaultObject", key="Char1")
        self.char2 = create_object("evennia.objects.objects.DefaultObject", key="Char2")
        self.character = self.char1
        self.combathandler = combat_base.TestAdvCombatBaseHandler.get_or_create_combathandler(self.character)

    def test_get_or_create_combathandler(self):
        """
        Test that we can get or create the handler.
        """
        self.assertTrue(bool(self.combathandler))
        self.assertTrue(self.combathandler.key == "combathandler")
        
        # Test getting the existing one
        combathandler2 = combat_base.TestAdvCombatBaseHandler.get_or_create_combathandler(self.character)
        self.assertEqual(self.combathandler, combathandler2)
        
    def test_msg(self):
        """
        Test sending messages.
        """
        self.combathandler.msg("Test message")
        # Since we can't easily capture the output to the session in this unit test without 
        # complex mocking of msg_contents, we mainly ensure it runs without error.
        
    def test_get_combat_summary(self):
        """
        Test getting the combat summary.
        """
        # Mock get_sides since it raises NotImplementedError in the base class
        self.combathandler.get_sides = MagicMock(return_value=([self.char1], [self.char2]))
        
        # Mock hurt levels
        self.char1.hurt_level = "Fine"
        self.char2.hurt_level = "Wounded"
        
        summary = self.combathandler.get_combat_summary(self.char1)
        self.assertTrue(bool(summary))
        self.assertIn("Fine", str(summary))
        self.assertIn("Wounded", str(summary))


class TestCombatActions(EvenniaTestCase):
    """
    Test the combat actions.
    """

    def setUp(self):
        super().setUp()
        self.char1 = create_object("evennia.objects.objects.DefaultObject", key="Char1")
        self.char2 = create_object("evennia.objects.objects.DefaultObject", key="Char2")
        self.attacker = self.char1
        self.target = self.char2
        self.combathandler = combat_base.TestAdvCombatBaseHandler.get_or_create_combathandler(self.attacker)
        
        # Mock the handler methods that are not implemented in the base class
        self.combathandler.has_advantage = MagicMock(return_value=False)
        self.combathandler.has_disadvantage = MagicMock(return_value=False)
        self.combathandler.give_advantage = MagicMock()
        self.combathandler.give_disadvantage = MagicMock()
        self.combathandler.msg = MagicMock()
        
        # Give attacker a weapon
        self.weapon = create_object(objects.TestAdvWeapon, key="Sword", location=self.attacker)
        self.attacker.weapon = self.weapon
        
        # Mock weapon use to avoid needing full equipment/rules integration in this unit test
        self.weapon.at_pre_use = MagicMock(return_value=True)
        self.weapon.use = MagicMock()
        self.weapon.at_post_use = MagicMock()

    def test_action_attack(self):
        """
        Test the attack action.
        """
        action_dict = {
            "key": "attack",
            "target": self.target
        }
        action = combat_base.CombatActionAttack(self.combathandler, self.attacker, action_dict)
        
        action.execute()
        
        # Check that weapon.use was called with the correct parameters (including our fix!)
        self.weapon.use.assert_called_with(
            self.attacker,
            self.target,
            attacker_advantage=False,
            attacker_disadvantage=False
        )
        self.weapon.at_post_use.assert_called_with(self.attacker, self.target)

    @patch("testadv.rules.dice.opposed_saving_throw")
    def test_action_stunt_success_advantage(self, mock_opposed_save):
        """
        Test a successful stunt giving advantage.
        """
        # Setup mock return: success=True, quality=None, txt="Success!"
        mock_opposed_save.return_value = (True, None, "Success!")
        
        action_dict = {
            "key": "stunt",
            "recipient": self.attacker, # giving self advantage
            "target": self.target,
            "advantage": True,
            "stunt_type": rules.Ability.PHYS,
            "defense_type": rules.Ability.COOR
        }
        action = combat_base.CombatActionStunt(self.combathandler, self.attacker, action_dict)
        
        action.execute()
        
        # Check if give_advantage was called
        self.combathandler.give_advantage.assert_called_with(self.attacker, self.target)
        
        # Verify the call to opposed_saving_throw matched our fix
        mock_opposed_save.assert_called_with(
            self.attacker,
            self.target, # target defends because we are giving advantage against them
            attack_type=rules.Ability.PHYS,
            defense_type=rules.Ability.COOR,
            attacker_advantage=False,
            attacker_disadvantage=False,
            defender_advantage=False,
            defender_disadvantage=False
        )

    @patch("testadv.rules.dice.opposed_saving_throw")
    def test_action_stunt_success_disadvantage(self, mock_opposed_save):
        """
        Test a successful stunt giving disadvantage to enemy.
        """
        mock_opposed_save.return_value = (True, None, "Success!")
        
        action_dict = {
            "key": "stunt",
            "recipient": self.target, # giving target disadvantage
            "target": self.target, # against themselves? or just generally? 
                                   # In combat_base: defender = target if advantage else recipient
                                   # if advantage=False (disadvantage), defender = recipient (target)
            "advantage": False,
            "stunt_type": rules.Ability.REAS,
            "defense_type": rules.Ability.WILL
        }
        action = combat_base.CombatActionStunt(self.combathandler, self.attacker, action_dict)
        
        action.execute()
        
        self.combathandler.give_disadvantage.assert_called_with(self.target, self.target)

    @patch("testadv.rules.dice.opposed_saving_throw")
    def test_action_stunt_failure(self, mock_opposed_save):
        """
        Test a failed stunt.
        """
        mock_opposed_save.return_value = (False, None, "Fail!")
        
        action_dict = {
            "key": "stunt",
            "recipient": self.attacker,
            "target": self.target,
            "advantage": True,
            "stunt_type": rules.Ability.PHYS,
            "defense_type": rules.Ability.COOR
        }
        action = combat_base.CombatActionStunt(self.combathandler, self.attacker, action_dict)
        
        action.execute()
        
        # Should NOT give advantage
        self.combathandler.give_advantage.assert_not_called()