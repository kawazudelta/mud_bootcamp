from evennia.utils import create
from evennia.utils.test_resources import BaseEvenniaTest

from ..objects import TestAdvObject, TestAdvArmor, TestAdvHelmet, TestAdvWeapon, TestAdvShield, TestAdvRuneStone, WeaponBareHands, TestAdvBodyArmor
from ..enums import WieldLocation, Ability
from ..characters import TestAdvCharacter

class TestEquipment(BaseEvenniaTest):
    
    def setUp(self):
        super().setUp() # Call parent setUp for proper test environment initialization
        # we're going to need a guy and some items
        self.character = create.create_object(TestAdvCharacter, key="testchar")
        self.helmet = create.create_object(TestAdvHelmet, key="helmet")
        self.armor = create.create_object(TestAdvBodyArmor, key="armor")
        self.weapon = create.create_object(TestAdvWeapon, key="weapon")
        self.shield = create.create_object(TestAdvShield, key="shield")
        self.runestone = create.create_object(TestAdvRuneStone, key="runestone")


    def test_count_slots(self):
        # real easy, testchar's inventory should be empty to start
        self.assertEqual(self.character.equipment.count_slots(), 0)

    def test_max_slots(self):
        #based on our system, PHYS and REAS both =1, so slots should =2 right now
        setattr(self.character, Ability.PHYS.value, 15)
        setattr(self.character, Ability.REAS.value, 8)
        # combining these two should get us up to 23 slots
        self.assertEqual(self.character.equipment.max_slots, 23)

    def test_add_remove(self):
        # test for helmet going into the backpack and being removed
        self.character.equipment.add(self.helmet)
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.BACKPACK],
            [self.helmet]
        )
        self.character.equipment.remove(self.helmet)
        self.assertEqual(self.character.equipment.slots[WieldLocation.BACKPACK], [])

    def test_move(self):
        # Give my man a sword
        self.character.equipment.add(self.weapon)
        # It should go into man's backpack
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.BACKPACK],
            [self.weapon]
        )
        self.character.equipment.move(self.weapon)
        # man should be gripped up on that sword
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.WEAPON_HAND],
            self.weapon
        )
        # now give man a runestone
        self.character.equipment.add(self.runestone)
        # should be the only thing in the backpack now
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.BACKPACK],
            [self.runestone]
        )
        # Now we equip the runestone, which should also unequip the sword
        self.character.equipment.move(self.runestone)
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.TWO_HANDS],
            self.runestone
        )
        # check sword not in WEAPON_HAND
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.WEAPON_HAND],
            None
        )
        # check sword returned to backpack
        self.assertEqual(
            self.character.equipment.slots[WieldLocation.BACKPACK],
            [[self.weapon]]
        )

    def test_all(self):
        # check for empty inventory (gem told me to, guess I should)
        all_items_empty = self.character.equipment.all()
        # Should contain 5 tuples for default slots, all with None
        self.assertEqual(len(all_items_empty), 5)
        self.assertIn((None, WieldLocation.WEAPON_HAND), all_items_empty)

        # put a helmet in the backpack
        self.character.equipment.add(self.helmet)
        all_items_backpack = self.character.equipment.all()
        # now there should be a helmet in the backpack
        self.assertIn((self.helmet, WieldLocation.BACKPACK), all_items_backpack)
        self.assertEqual(len(all_items_backpack), 6) # 5 fixed slots + 1 backpack item

        # make a sword and equip it
        self.character.equipment.add(self.weapon)
        self.character.equipment.move(self.weapon)
        all_items_equipped = self.character.equipment.all()

        # Check that the sword is now in the WEAPON_HAND slot
        self.assertIn((self.weapon, WieldLocation.WEAPON_HAND), all_items_equipped)
        # Check that it's no longer in the backpack (if it was added there first)
        self.assertNotIn((self.weapon, WieldLocation.BACKPACK), all_items_equipped)

        # Check exact inventory contents
        expected_list = [
            (self.weapon, WieldLocation.WEAPON_HAND),
            (None, WieldLocation.SHIELD_HAND),
            (None, WieldLocation.TWO_HANDS),
            (None, WieldLocation.BODY),
            (None, WieldLocation.HEAD),
            (self.helmet, WieldLocation.BACKPACK), # assuming helmet is still in backpack
        ]
        self.assertCountEqual(all_items_equipped, expected_list)

    def test_armor(self):
        # test the armor calculation based on default shield and helmet
        self.character.equipment.move(self.shield)
        # Expected: 1 (shield) + 1 (default body) + 1 (default head) = 3
        self.assertEqual(self.character.equipment.armor, 3)
        self.character.equipment.move(self.helmet)
        # Expected: 1 (shield) + 1 (helmet) + 1 (default body) = 3
        self.assertEqual(self.character.equipment.armor, 3)
        setattr(self.armor, "armor", 11) # Explicitly set armor value for the test
        # equip it
        self.character.equipment.move(self.armor)
        # Expected: 11 (body armor) + 1 (shield) + 1 (helmet) = 13
        self.assertEqual(self.character.equipment.armor, 13)

    def test_weapon(self):
        #check if character is wielding a two-hander, a one hander, or bare hands
        self.character.equipment.move(self.runestone)
        self.assertEqual(self.character.equipment.weapon, self.runestone)
        self.character.equipment.move(self.weapon)
        self.assertEqual(self.character.equipment.weapon, self.weapon)
        # unequip the weapon to check for bare hands
        self.character.equipment.remove(self.weapon)
        expected_bare_hands = WeaponBareHands.get_bare_hands()
        self.assertEqual(self.character.equipment.weapon, expected_bare_hands)