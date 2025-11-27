from copy import deepcopy
from random import choice, random

from evennia import AttributeProperty, DefaultRoom, DefaultCharacter, TICKER_HANDLER
from evennia.utils.utils import inherits_from

CHAR_SYMBOL = "|w@|n"
CHAR_ALT_SYMBOL = "|w>|n"
ROOM_SYMBOL = "|bo|n"
LINK_COLOR = "|B"

_MAP_GRID = [
    [" ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " "],
    [" ", " ", "@", " ", " "],
    [" ", " ", " ", " ", " "],
    [" ", " ", " ", " ", " "],
]

_EXIT_GRID_SHIFT = {
    "north": (0, 1, "||"),
    "east": (1, 0, "-"),
    "south": (0, -1, "||"),
    "west": (-1, 0, "-"),
    "northeast": (1, 1, "/"),
    "southeast": (1, -1, "\\"),
    "southwest": (-1, -1, "/"),
    "northwest": (-1, 1, "\\"),
}


class TestAdvRoom(DefaultRoom):
    '''
    Simple room supporting some TestAdv specifics
    '''
    allow_combat = AttributeProperty(False, autocreate=False)
    allow_pvp = AttributeProperty(False, autocreate=False)
    allow_death = AttributeProperty(False, autocreate=False)

    def format_appearance(self, appearance, looker, **kwargs):
        '''
        Don't left strip the appearance string
        '''
        return appearance.rstrip()
    
    def get_display_header(self, looker, **kwargs):
        '''
        Display the current location as a mini-map
        '''
        # make sure not to show map for anyone using a screenreader
        # for optimization we also don't need to show it to NPCs or mobs
        if not inherits_from(looker, DefaultCharacter) or (looker.account and looker.account.uses_screenreader()
        ):
            return ""

        # otherwise build a map
        map_grid = deepcopy(_MAP_GRID)
        dx0, dy0 = 2, 2
        map_grid[dy0][dx0] = CHAR_SYMBOL
        for exi in self.exits:
            dx, dy, symbol = _EXIT_GRID_SHIFT.get(exi.key, (None, None, None))
            if symbol is None:
                # That is, if we have a non-cardinal direction (an exit or up/down in/out)
                map_grid[dy0][dx0] = CHAR_ALT_SYMBOL
                continue
            map_grid[dy0 + dy][dx0 + dx] = f"{LINK_COLOR}{symbol}|n"
            if exi.destination != self:
                map_grid[dy0 + dy + dy][dx0 + dx + dx] = ROOM_SYMBOL

        # Note that on the grid, dy is really going *downwards* (origo is
        # in the top left), so we need to reverse the order at the end to mirror it
        # vertically and have it come out right.
        # ^^^ Because it's a series of lists, so y increases downward, instead of upward
        return "  " + "\n  ".join("".join(line) for line in reversed(map_grid))


class TestAdvPVPRoom(TestAdvRoom):
    '''
    Room where you can PVP but non-lethal only
    '''
    allow_combat = AttributeProperty(True, autocreate=False)
    allow_pvp = AttributeProperty(True, autocreate=False)

    def get_display_footer(self, looker, **kwargs):
        '''
        customize footer of description
        '''
        return "|yNon-lethal PvP combat is allowed here!|n"
    

class EchoingRoom(TestAdvRoom):
    '''
    A room that randomly echoes messages to everyone inside it
    '''
    echoes = AttributeProperty(False, autocreate=False)
    echo_rate = AttributeProperty(60 * 2, autocreate=False)
    echo_chance = AttributeProperty(0.1, autocreate=False)

    def send_echo(self):
        if self.echoes and random() < self.echo_chance:
            self.msg_contents(choice(self.echoes))

    def start_echo(self):
        TICKER_HANDLER.add(self.echo_rate, self.send_echo)

    def stop_echo(self):
        TICKER_HANDLER.remove(self.echo_rate, self.send_echo)