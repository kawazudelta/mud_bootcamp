from evennia.typeclasses.attributes import AttributeProperty
from evennia.objects.objects import DefaultExit

from .rooms import TestAdvRoom

class TestAdvDungeonRoom(TestAdvRoom):
    '''
    dangerous dungeon room.
    '''
    allow_combat = AttributeProperty(True, autocreate=False)
    allow_death = AttributeProperty(True, autocreate=False)

    # dungeon generation attributes, set on room creation
    dungeon_branch = AttributeProperty(None, autocreate=False)
    xy_coords = AttributeProperty(None, autocreate=False)

    def at_object_creation(self):
        '''Set the `not_clear` tag on the room. This is removed when the room is
        'cleared', whatever that means for each room.

        We put this here rather than in the room-creation code so we can override
        easier (for example we may want an empty room which auto-clears).
        '''
        self.tags.add("not_clear", category="dungeon_room")

    def clear_room(self):
        self.tags.remove("not_clear", category="dungeon_room")

    @property
    def is_room_clear(self):
        return not bool(self.tags.get("not_clear", category="dungeon_room"))
    
    def get_display_footer(self, looker, **kwargs):
        '''
        Show if the room is 'cleared' or not as part of its description.
        '''
        if self.is_room_clear:
            return ""
        else:
            return "|rThe path forwards is blocked!|n"
        
class TestAdvDungeonExit(DefaultExit):
    '''
    A custom exit for the dungeon. Creates the next room as it's traversed!
    '''
    def at_object_creation(self):
        """
        We want to block progressing forward unless the room is clear.

        """
        self.locks.add("traverse:not objloctag(not_clear, dungeon_room)")

    def at_traverse(self, traversing_object, target_location, **kwargs):
        """
        Called when traversing. `target_location` will be pointing back to ourselves if the target
        was not yet created. It checks the current location to get the dungeon-branch in use.

        """
        # dungeon_branch = self.location.db.dungeon_branch
        # if target_location == self.location:
        #     # destination points back to us - create a new room
        #     self.destination = target_location = dungeon_branch.new_room(self)
        #     dungeon_branch.register_exit_traversed(self)

        # super().at_traverse(traversing_object, target_location, **kwargs)

        # TODO not at that point in the tutorial yet
        pass
    
    def at_failed_traverse(self, traversing_object, **kwargs):
        """
        Called when failing to traverse.

        """
        traversing_object.msg("You can't get through this way yet!")
    