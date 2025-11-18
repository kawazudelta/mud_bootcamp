from evennia.utils import create
from evennia.utils.test_resources import BaseEvenniaTest

from ..characters import TestAdvCharacter

class TestCharacters(BaseEvenniaTest):
    def setUp(self):
        super().setUp()
        self.character = create.create_object(TestAdvCharacter, key="testchar")

    def test_abilities(self):
        # Making sure our abilities go up.
        self.character.physique += 2
        self.assertEqual(self.character.physique, 3)

        # And go down
        self.character.physique -= 2
        self.assertEqual(self.character.physique, 1)

    def test_heal(self):
        # set up our dummy
        self.character.hp = 0
        self.character.hp_max = 10

        # make sure we can heal 1 HP
        self.character.heal(1)
        self.assertEqual(self.character.hp, 1)
        
        # make sure we can't heal past our max
        self.character.heal(100)
        self.assertEqual(self.character.hp, 10)

    def test_at_damage(self):
        # Test that we can hurt the character
        self.character.hp = 8
        self.character.at_damage(5)
        self.assertEqual(self.character.hp, 3)

    def test_at_pay(self):
        self.character.coins = 100

        #test that if we pay 60 coins for something, we're left with 40
        result = self.character.at_pay(60)
        self.assertEqual(result, 60)
        self.assertEqual(self.character.coins, 40)

        #test that if we pay more than we have, we stop at 0 coins
        result = self.character.at_pay(100)
        self.assertEqual(result, 40)
        self.assertEqual(self.character.coins, 0)