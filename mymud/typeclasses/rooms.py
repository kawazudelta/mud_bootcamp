"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils import list_to_string, utils, english

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    def return_appearance(self, looker, **kwargs):
        """
        This formats a description. It is the hook a 'look' command
        should call.

        Args:
            looker (Object): The object looking at this object.
            **kwargs (dict): Arbitrary, optional arguments for users
                overriding the hook. It is passed on to the hook.

        Returns:
            str: The description of this object.
        """
        if not looker:
            return ""

        # Get and identify all objects
        visible = [con for con in self.contents if con != looker and con.access(looker, "view")]
        exits = [con for con in self.exits if con.access(looker, "view")]
        
        # Get descriptions of things
        string = "|c%s|n\n" % self.get_display_name(looker)
        desc = self.db.desc
        if desc:
            string += "%s" % desc

        # List exits
        exit_strings = []
        for exit in exits:
            exit_strings.append(exit.get_display_name(looker))
        if exit_strings:
            string += "\n\n|wExits:|n " + list_to_string(exit_strings)

        # Get characters and objects
        character_list = [char.get_display_name(looker) for char in visible if char.has_account]
        object_list = [obj for obj in visible if not obj.has_account]

        # Format and list characters
        if character_list:
            string += "\n\n|wYou see:|n " + list_to_string(character_list)

        # Format and list objects
        if object_list:
            formatted_object_strings = []
            for item in object_list:
                item_name = item.get_display_name(looker)
                # Check if the name already starts with an article
                if item_name.lower().startswith(("a ", "an ", "the ")):
                    formatted_object_strings.append(item_name)
                else:
                    # Use Evennia's utility to add the correct article
                    formatted_object_strings.append(f"{english.get_indefinite_article(item_name)} {item_name}")
            
            if not character_list:
                # If no characters, start a new "You see:" line
                string += "\n\n|wYou see:|n " + list_to_string(formatted_object_strings)
            else:
                # If characters are already listed, append objects with a comma
                string += ", " + list_to_string(formatted_object_strings)

        return string

