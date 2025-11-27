from evennia import create_object                                           
from evennia.utils.test_resources import EvenniaTest                        
                                                                            
from .. import npcs                                                         
                                                                            
class TestNPCBase(EvenniaTest):
    '''
    Test the NPC base class
    '''
        
    def test_npc_base(self):
        npc = create_object(
            npcs.TestAdvNPC,
            key="TestNPC",
            attributes=[("hit_dice", 4)],  # set hit_dice to 4
        )
        
        # attributes are set after at_object_creation, so we need to recalculate hp
        npc.hp = npc.max_hp

        self.assertEqual(npc.hp_multiplier, 4)
        self.assertEqual(npc.hp, 16)
        self.assertEqual(npc.physique, 14)
        self.assertEqual(npc.willpower, 14)