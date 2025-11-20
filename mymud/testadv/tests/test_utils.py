from evennia.utils import create
from evennia.utils.test_resources import BaseEvenniaTest

from .. import utils
from ..objects import TestAdvObject

class TestUtils(BaseEvenniaTest):
    def test_get_obj_stats(self):
        # make a simple object to test with
        obj = create.create_object(
            TestAdvObject,
            key="testobj",
            attributes=(("desc", "A test object"),)
        )
        # run it through the function
        result = utils.get_obj_stats(obj)  
        # check that the result is what we expected
        self.assertEqual(
            result,
            """
|ctestobj|n
Value: ~|y0|n coins

A test object

Slots: |w1|n, Used from: |wbackpack|n
Quality: |wN/A|n, Uses: |wN/A|n
Attacks using |wNo attack|n against |wNo defense|n
Damage roll: |wNone|n
""".strip()
)