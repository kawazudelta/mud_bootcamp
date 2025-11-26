from unittest.mock import MagicMock, patch
from evennia.utils.test_resources import BaseEvenniaTest
from ..chargen import (
    TemporaryCharacterSheet, 
    node_chargen, 
    node_name_change,
    _update_name, 
    _swap_abilities, 
    node_apply_character,
    _ABILITIES
)
from ..characters import TestAdvCharacter

class TestChargen(BaseEvenniaTest):
    """
    Test the character generation module.
    """

    def setUp(self):
        super().setUp()
        self.tmp_char = TemporaryCharacterSheet()

    def test_temp_character_sheet_init(self):
        """
        Test that TemporaryCharacterSheet initializes with valid values.
        """
        sheet = self.tmp_char
        
        # Check abilities are >= 7 (as per the deviation in chargen.py)
        for ability in _ABILITIES.values():
            val = getattr(sheet, ability)
            self.assertIsInstance(val, int)
            self.assertGreaterEqual(val, 7)

        # Check basic stats
        self.assertTrue(sheet.name)
        self.assertEqual(sheet.level, 1)
        self.assertEqual(sheet.xp, 0)
        self.assertGreater(sheet.hp_max, 0)
        self.assertEqual(sheet.hp, sheet.hp_max)

        # Check equipment lists
        self.assertIsInstance(sheet.backpack, list)
        self.assertEqual(len(sheet.backpack), 6)  # 2 rations + 4 random items
        self.assertTrue(sheet.weapon)

    def test_show_sheet(self):
        """
        Test the string representation of the sheet.
        """
        text = self.tmp_char.show_sheet()
        self.assertIn(self.tmp_char.name, text)
        self.assertIn(str(self.tmp_char.physique), text)
        self.assertIn("Your belongings:", text)

    @patch("testadv.chargen.dice.roll_random_table")
    @patch("testadv.chargen.dice.roll")
    def test_init_description_deterministic(self, mock_roll, mock_roll_table):
        """
        Test that the description is built correctly using deterministic mocks.
        """
        # We need to mock the returns for the __init__ call of TemporaryCharacterSheet.
        # It calls roll("3d6") 6 times for stats, "1d8" for hp.
        mock_roll.return_value = 10 
        
        # roll_random_table is called for:
        # name (1), bodytype, face, skin, hair, clothing, speech, virtue, vice, background, misfortune, alignment (11)
        # armor, helm/shield, weapon (3)
        # backpack items (4)
        
        # We'll provide a side_effect for roll_random_table to return specific strings for the description parts
        # Order in __init__:
        # name, [stats handled by roll], bodytype, face, skin, hair, clothing, speech, virtue, vice, background, misfortune, alignment
        # ...
        
        mock_roll_table.side_effect = [
            "TestName",       # name
            "athletic",       # bodytype
            "chiseled",       # face
            "pale",           # skin
            "bald",           # hair
            "elegant",        # clothing
            "blunt",          # speech
            "honest",         # virtue
            "greedy",         # vice
            "cook",           # background
            "cursed",         # misfortune
            "neutrality",     # alignment
            "gambeson",       # armor
            "helmet",         # helmet/shield
            "club",           # weapon
            "rope", "torch", "pick", "flint" # backpack items
        ]

        sheet = TemporaryCharacterSheet()
        
        expected_desc = (
            "You are athletic with a chiseled face, pale skin, bald hair, blunt speech, "
            "and elegant clothing. You were a Cook, but you were cursed and ended up a knave. "
            "You are honest but also greedy. You are of the neutrality alignment."
        )
        
        self.assertEqual(sheet.desc, expected_desc)
        self.assertEqual(sheet.name, "TestName")

    @patch("testadv.chargen.spawn")
    @patch("testadv.chargen.create_object")
    def test_apply(self, mock_create_object, mock_spawn):
        """
        Test the application of the temporary sheet to a real character.
        """
        # Setup mocks
        mock_new_char = MagicMock()
        mock_create_object.return_value = mock_new_char
        
        # Mock the spawned items so they are not None
        mock_spawn.return_value = [MagicMock()] 

        # Call apply
        result = self.tmp_char.apply()

        # Check create_object called with correct class and attributes
        mock_create_object.assert_called_once()
        args, kwargs = mock_create_object.call_args
        self.assertEqual(args[0], TestAdvCharacter)
        self.assertEqual(kwargs['key'], self.tmp_char.name)
        
        # Check that attributes dict contains our stats
        attrs = dict(kwargs['attrs'])
        self.assertEqual(attrs['physique'], self.tmp_char.physique)
        self.assertEqual(attrs['hp'], self.tmp_char.hp)

        # Check that spawn was called for equipment
        self.assertTrue(mock_spawn.called)
        
        # Check that items were moved to equipment
        # Note: apply() calls spawn() which returns a list, even for single items usually
        # but the code says: weapon = spawn(self.weapon); new_character.equipment.move(weapon)
        # So we verify move/add was called on the equipment handler
        self.assertTrue(mock_new_char.equipment.move.called or mock_new_char.equipment.add.called)
        self.assertEqual(result, mock_new_char)

    def test_node_chargen(self):
        """
        Test the main chargen menu node.
        """
        text, options = node_chargen(self.char1, "", tmp_character=self.tmp_char)
        
        # Check text contains sheet info
        self.assertIn(self.tmp_char.name, text)
        
        # Check options
        option_keys = [opt['desc'] for opt in options]
        self.assertIn("Change your name", option_keys)
        self.assertIn("Accept and create character", option_keys)
        
        # Verify goto for name change
        name_opt = next(o for o in options if o['desc'] == "Change your name")
        self.assertEqual(name_opt['goto'][0], "node_name_change")
        
        # Verify swap ability option exists initially
        self.assertIn("Swap two of your ability scores (once)", option_keys)

        # Verify swap option disappears after use
        self.tmp_char.ability_changes = 1
        text, options = node_chargen(self.char1, "", tmp_character=self.tmp_char)
        option_keys = [opt['desc'] for opt in options]
        self.assertNotIn("Swap two of your ability scores (once)", option_keys)

    def test_node_name_change(self):
        """
        Test the name change node.
        """
        text, options = node_name_change(self.char1, "", tmp_character=self.tmp_char)
        self.assertIn(self.tmp_char.name, text)
        self.assertIn("Enter a new name", text)
        
        # Check goto matches the helper
        self.assertEqual(options["goto"][0], _update_name)

    def test_update_name(self):
        """
        Test the name update helper.
        """
        next_node, kwargs = _update_name(self.char1, "Conan", tmp_character=self.tmp_char)
        self.assertEqual(next_node, "node_chargen")
        self.assertEqual(self.tmp_char.name, "Conan")

    def test_swap_abilities_valid(self):
        """
        Test swapping abilities with valid input.
        """
        # Set specific values to test swap
        self.tmp_char.physique = 10
        self.tmp_char.willpower = 15
        self.tmp_char.ability_changes = 0

        next_node, kwargs = _swap_abilities(self.char1, "PHYS WILL", tmp_character=self.tmp_char)
        
        self.assertEqual(next_node, "node_chargen")
        self.assertEqual(self.tmp_char.physique, 15)
        self.assertEqual(self.tmp_char.willpower, 10)
        self.assertEqual(self.tmp_char.ability_changes, 1)

    def test_swap_abilities_invalid(self):
        """
        Test swapping abilities with invalid input.
        """
        original_phys = self.tmp_char.physique
        self.tmp_char.ability_changes = 0

        # Invalid ability name
        next_node, kwargs = _swap_abilities(self.char1, "PHYS MAGIC", tmp_character=self.tmp_char)
        
        # Should return None (which keeps user in same node/calls it again usually, 
        # but specifically _swap_abilities returns None, kwargs on failure in the provided code)
        self.assertIsNone(next_node)
        self.assertEqual(self.tmp_char.physique, original_phys)
        self.assertEqual(self.tmp_char.ability_changes, 0)

        # Malformed string
        next_node, kwargs = _swap_abilities(self.char1, "PHYS", tmp_character=self.tmp_char)
        self.assertIsNone(next_node)

    def test_node_apply_character(self):
        """
        Test the final node that applies the character.
        """
        # Ensure account is linked (BaseEvenniaTest usually does this, but to be safe)
        if not self.char1.account:
            self.char1.account = self.account

        # Mock apply on the tmp_character to return a new character object
        new_char_mock = MagicMock()
        self.tmp_char.apply = MagicMock(return_value=new_char_mock)

        # Patch the characters.add method on the account object
        # We need to access the handler instance. 
        # Since it's a lazy property or handler, getting it should work.
        # We assume self.char1.account.characters returns a handler object.
        
        # NOTE: patching specific attributes on complex Django/Evennia objects can be tricky 
        # if they are created on the fly.
        # However, let's try to just mock the 'add' method on the handler instance.
        
        with patch.object(self.char1.account.characters, 'add') as mock_add_char:
            text, options = node_apply_character(self.char1, "", tmp_character=self.tmp_char)

            # Verify apply was called
            self.tmp_char.apply.assert_called_once()
            
            # Verify character was added to account
            mock_add_char.assert_called_with(new_char_mock)
            
            # Verify menu exit (options is None)
            self.assertIsNone(options)
            self.assertEqual(text, "Character created!")
