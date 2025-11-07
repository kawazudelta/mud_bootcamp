from evennia import Command, CmdSet

class CmdSit(Command):
    '''
    Sit down.
    '''
    key = "sit"
    def func(self):
        self.obj.do_sit(self.caller)

class CmdStand(Command):
    '''
    Stand up.
    '''
    key = "stand"
    locks = "cmd:sitonthis()"
    
    def func(self):
        self.obj.do_stand(self.caller)

class CmdSetSit(CmdSet):
    priority = 1
    def at_cmdset_creation(self):
        self.add(CmdSit)
        self.add(CmdStand)

class CmdNoSitStand(Command):
    '''
    Sit down or Stand up
    '''
    key = "sit"
    aliases = ["Stand"]

    def func(self):
        if self.cmdname == "sit":
            self.msg("You have nothing to sit on.")
        else:
            self.msg("You are not sitting down.")