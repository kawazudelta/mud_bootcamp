"""
Tests for the combat system.
"""

from unittest.mock import MagicMock, patch
from evennia import create_object
from evennia.utils.test_resources import EvenniaTestCase
from .. import combat_base
from .. import combat_twitch
from .. import rules 
from .. import objects 
from .. import characters
from .. import npcs

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
            "target": self.target,
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

    def test_action_use_item(self):
        """
        Test the use item action.
        """
        # Create a mock item
        item = create_object("evennia.objects.objects.DefaultObject", key="Potion", location=self.attacker)
        item.at_pre_use = MagicMock(return_value=True)
        item.use = MagicMock()
        item.at_post_use = MagicMock()
        
        action_dict = {
            "key": "use",
            "item": item,
            "target": self.target
        }
        action = combat_base.CombatActionUseItem(self.combathandler, self.attacker, action_dict)
        
        action.execute()
        
        item.use.assert_called_with(
            self.attacker,
            self.target,
            advantage=False,
            disadvantage=False
        )
        item.at_post_use.assert_called_with(self.attacker, self.target)

    def test_action_wield(self):
        """
        Test the wield action.
        """
        # Create a new weapon to wield
        new_weapon = create_object("evennia.objects.objects.DefaultObject", key="Axe", location=self.attacker)
        
        # Mock the equipment handler on the attacker
        self.attacker.equipment = MagicMock()
        self.attacker.equipment.move = MagicMock()

        action_dict = {
            "key": "wield",
            "item": new_weapon
        }
        action = combat_base.CombatActionWield(self.combathandler, self.attacker, action_dict)
        
        action.execute()
        
        self.attacker.equipment.move.assert_called_with(new_weapon)


class TestTwitchCombatHandler(EvenniaTestCase):
    """
    Test the Twitch (real-time-ish) combat handler.
    """

    def setUp(self):
        super().setUp()
        self.room = create_object("evennia.objects.objects.DefaultRoom", key="Room")
        self.char1 = create_object(characters.TestAdvCharacter, key="PC", location=self.room)
        self.char2 = create_object(npcs.TestAdvNPC, key="NPC", location=self.room)
        
        # Ensure HP is set
        self.char1.hp = 10
        self.char2.hp = 10

        self.handler = combat_twitch.TestAdvCombatTwitchHandler.get_or_create_combathandler(self.char1)
        # Ensure handler is saved to DB so AttributeProperties work
        if not self.handler.id:
            self.handler.save()

    def test_get_sides_pve(self):
        """
        Test get_sides in PvE (PC vs NPC).
        """
        # Make sure char2 has a handler too so it's recognized as a combatant
        combat_twitch.TestAdvCombatTwitchHandler.get_or_create_combathandler(self.char2)

        allies, enemies = self.handler.get_sides(self.char1)
        
        # char1 is PC, char2 is NPC. 
        # In PvE (default), PCs vs NPCs.
        self.assertIn(self.char2, enemies)
        self.assertNotIn(self.char1, enemies)
        self.assertNotIn(self.char1, allies) 

    def test_get_sides_pvp(self):
        """
        Test get_sides in PvP.
        """
        self.room.allow_pvp = True
        combat_twitch.TestAdvCombatTwitchHandler.get_or_create_combathandler(self.char2)
        
        allies, enemies = self.handler.get_sides(self.char1)
        
        # In PvP, everyone else is enemy
        self.assertIn(self.char2, enemies)
        self.assertIn(self.char1, allies) # Code says: allies = [combatant]

    def test_advantage_disadvantage(self):
        """
        Test tracking of advantage/disadvantage.
        """
        self.handler.give_advantage(self.char1, self.char2)
        self.assertTrue(self.handler.has_advantage(self.char1, self.char2))
        
        self.handler.give_disadvantage(self.char1, self.char2)
        self.assertTrue(self.handler.has_disadvantage(self.char1, self.char2))

    @patch("testadv.combat_twitch.repeat")
    @patch("testadv.combat_twitch.unrepeat")
    def test_queue_action(self, mock_unrepeat, mock_repeat):
        """
        Test queueing an action.
        """
        mock_repeat.return_value = 123
        
        action_dict = {"key": "attack", "target": self.char2, "dt": 3}
        self.handler.queue_action(action_dict)
        
        self.assertEqual(self.handler.action_dict, action_dict)
        self.assertEqual(self.handler.current_ticker_ref, 123)
        mock_repeat.assert_called_with(3, self.handler.execute_next_action, id_string="combat")

    @patch("testadv.combat_twitch.repeat")
    @patch("testadv.combat_twitch.unrepeat")
    def test_execute_next_action(self, mock_unrepeat, mock_repeat):
        """
        Test executing the next action.
        """
        # Setup action dict
        self.handler.action_dict = {
            "key": "attack",
            "target": self.char2,
            "dt": 3,
            "repeat": True
        }
        
        # Mock action class
        with patch.dict(self.handler.action_classes):
            mock_action_class = MagicMock()
            self.handler.action_classes["attack"] = mock_action_class
            
            mock_action_instance = mock_action_class.return_value
            mock_action_instance.can_use.return_value = True
            
            # Mock check_stop_combat
            self.handler.check_stop_combat = MagicMock()

            # Execute
            self.handler.execute_next_action()
            
            # Verify execution
            mock_action_instance.execute.assert_called()
            mock_action_instance.post_execute.assert_called()
            
            # Since repeat=True, should NOT queue fallback
            
    def test_execute_next_action_no_repeat(self):
        """
        Test executing a non-repeating action.
        """
        self.handler.action_dict = {
            "key": "stunt",
            "dt": 3,
            "repeat": False # Explicitly false
        }
        
        # Mock check_stop_combat to avoid side effects
        self.handler.check_stop_combat = MagicMock()

        # Mock action class
        with patch.dict(self.handler.action_classes):
            mock_action_class = MagicMock()
            self.handler.action_classes["stunt"] = mock_action_class
            mock_action_instance = mock_action_class.return_value
            mock_action_instance.can_use.return_value = True

            self.handler.execute_next_action()
            
            # Verify it fell back to hold
            self.assertEqual(self.handler.action_dict["key"], "hold")

    def test_check_stop_combat(self):
        """
        Test stopping combat when enemies are defeated.
        """
        # Mock get_sides
        self.handler.get_sides = MagicMock(return_value=([self.char1], [])) # No enemies
        
        # Mock stop_combat
        self.handler.stop_combat = MagicMock()
        self.handler.msg = MagicMock()
        
        self.handler.check_stop_combat()
        
        self.handler.stop_combat.assert_called()
        self.handler.msg.assert_any_call("None remain who oppose you.")
