"""
Helpers for testing testadv modules.

"""

from evennia.utils import create

from .. import enums
from ..characters import TestAdvCharacter
from ..objects import (
    TestAdvArmor,
    TestAdvHelmet,
    TestAdvObject,
    TestAdvShield,
    TestAdvWeapon,
)
from ..rooms import TestAdvRoom


class EvAdventureMixin:
    """
    Provides a set of pre-made characters.

    """

    def setUp(self):
        super().setUp()
        self.location = create.create_object(TestAdvRoom, key="testroom")
        self.character = create.create_object(
            TestAdvCharacter, key="testchar", location=self.location
        )
        self.helmet = create.create_object(
            TestAdvHelmet,
            key="helmet",
        )
        self.shield = create.create_object(
            TestAdvShield,
            key="shield",
        )
        self.armor = create.create_object(
            TestAdvArmor,
            key="armor",
        )
        self.weapon = create.create_object(
            TestAdvWeapon,
            key="weapon",
        )
        self.big_weapon = create.create_object(
            TestAdvWeapon,
            key="big_weapon",
            attributes=[("inventory_use_slot", enums.WieldLocation.TWO_HANDS)],
        )
        self.item = create.create_object(TestAdvObject, key="backpack item")
