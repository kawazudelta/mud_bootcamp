from commands.command import Command
from evennia import CmdSet


class CmdEcho(Command):
    '''
    A simple echo command
    
    Usage:
        echo <something>
    '''
    key = "echo"

    def func(self):
        self.caller.msg(f"Echo: '{self.args.strip()}'")


class CmdHit(Command):
    '''
    Hit a target.
    
    Usage:
        hit <target>
    '''
    key = "hit"

    def func(self):
        args = self.args.strip()
        if not args:
            self.caller.msg("Who do you want to hit?")
            return
        target = self.caller.search(args)
        if not target:
            return
        self.caller.msg(f"You hit {target.key} with full force!")
        target.msg(f"You got hit by {self.caller.key} with full force!")


class MyCmdSet(CmdSet):

    def at_cmdset_creation(self):
        self.add(CmdEcho)
        self.add(CmdHit)