"""
Tests for the AI system.
"""

from unittest.mock import MagicMock, patch
from evennia.utils.test_resources import EvenniaTestCase
from evennia import create_object
from .. import ai
from .. import npcs
from .. import characters
from .. import enums

class TestAI(EvenniaTestCase):
    """
    Test the AI handler and mixin.
    """

    def setUp(self):
        super().setUp()
        self.room = create_object("evennia.objects.objects.DefaultRoom", key="Room")
        self.room2 = create_object("evennia.objects.objects.DefaultRoom", key="Room2")
        self.exit = create_object("evennia.objects.objects.DefaultExit", key="out", location=self.room, destination=self.room2)
        
        # Mob
        self.mob = create_object(npcs.TestAdvMob, key="Mob", location=self.room)
        # PC
        self.pc = create_object(characters.TestAdvCharacter, key="PC", location=self.room)

        # AI Handler
        self.ai = self.mob.ai

    def test_init(self):
        """
        Test that the AI handler is initialized correctly.
        """
        self.assertEqual(self.ai.obj, self.mob)
        self.assertEqual(self.ai.get_state(), "idle") # Default state

    def test_set_state(self):
        """
        Test setting the AI state.
        """
        self.ai.set_state("combat")
        self.assertEqual(self.ai.get_state(), "combat")
        self.assertEqual(self.mob.attributes.get("ai_state", category="ai_state"), "combat")

    def test_get_targets(self):
        """
        Test getting targets.
        """
        targets = self.ai.get_targets()
        self.assertIn(self.pc, targets)
        self.assertNotIn(self.mob, targets)

    def test_get_traversable_exits(self):
        """
        Test getting traversable exits.
        """
        exits = self.ai.get_traversable_exits()
        self.assertIn(self.exit, exits)

        # Test exclude
        exits = self.ai.get_traversable_exits(exclude_destination=self.room2)
        self.assertNotIn(self.exit, exits)

    @patch("random.random")
    def test_random_probability(self, mock_random):
        """
        Test the weighted probability selector.
        """
        probs = {"a": 0.8, "b": 0.2}
        
        # Test "a" (0.0 to 0.8)
        mock_random.return_value = 0.5
        self.assertEqual(self.ai.random_probability(probs), "a")
        
        # Test "b" (0.8 to 1.0)
        mock_random.return_value = 0.9
        self.assertEqual(self.ai.random_probability(probs), "b")

    def test_run_idle(self):
        """
        Test running the AI in idle state.
        """
        self.ai.set_state("idle")
        # idle does nothing, just shouldn't crash
        self.ai.run()

    @patch("random.choice")
    def test_run_roam_find_target(self, mock_choice):
        """
        Test roaming finding a target.
        """
        self.ai.set_state("roam")
        mock_choice.return_value = self.pc
        
        # Mock execute_cmd
        self.mob.execute_cmd = MagicMock()
        
        self.ai.run()
        
        self.assertEqual(self.ai.get_state(), "combat")
        self.mob.execute_cmd.assert_called_with(f"attack {self.pc.key}")

    @patch("random.choice")
    def test_run_roam_no_target_move(self, mock_choice):
        """
        Test roaming with no target, moving to exit.
        """
        # Remove PC from room
        self.pc.location = self.room2
        
        self.ai.set_state("roam")
        mock_choice.return_value = self.exit
        
        self.mob.execute_cmd = MagicMock()
        
        self.ai.run()
        
        self.mob.execute_cmd.assert_called_with(f"{self.exit.key}")

    @patch("random.choice")
    def test_run_flee(self, mock_choice):
        """
        Test fleeing.
        """
        self.ai.set_state("flee")
        mock_choice.return_value = self.exit
        self.mob.execute_cmd = MagicMock()
        
        self.ai.run()
        
        self.mob.execute_cmd.assert_called_with(f"{self.exit.key}")
        # Should record past room
        self.assertEqual(self.mob.attributes.get("past_room", category="ai_state"), self.room)

    def test_run_combat_start(self):
        """
        Test combat state initiation (not yet in combat handler).
        """
        self.ai.set_state("combat")
        
        # Mock getting targets
        self.mob.execute_cmd = MagicMock()
        
        # Should attack a target if found
        with patch("random.choice", return_value=self.pc):
            self.ai.run()
            self.mob.execute_cmd.assert_called_with(f"attack {self.pc.key}")

    @patch("testadv.ai.AIHandler.random_probability")
    @patch("random.choice")
    def test_run_combat_in_combat(self, mock_choice, mock_prob):
        """
        Test combat state when already in combat handler.
        """
        self.ai.set_state("combat")
        
        # Mock combathandler on mob
        combathandler = MagicMock()
        self.mob.ndb.combathandler = combathandler
        
        # Mock sides
        combathandler.get_sides.return_value = ([self.mob], [self.pc])
        mock_choice.return_value = self.pc # Enemy choice
        
        # 1. Test Attack
        mock_prob.return_value = "attack"
        self.ai.run()
        combathandler.queue_action.assert_called_with({"key": "attack", "target": self.pc})
        
        # 2. Test Hold
        mock_prob.return_value = "hold"
        self.ai.run()
        combathandler.queue_action.assert_called_with({"key": "hold"})

        # 3. Test Stunt
        mock_prob.return_value = "stunt"
        mock_choice.return_value = self.mob # Ally choice (self)
        self.ai.run()
        combathandler.queue_action.assert_called_with({
            "key": "stunt",
            "recipient": self.mob,
            "advantage": True,
            "stunt_type": enums.Ability.PHYS,
            "defense_type": enums.Ability.COOR,
        })
