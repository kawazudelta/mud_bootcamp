# Objects you can sit on

from typeclasses.objects import Object
from commands.sittables import CmdSetSit

class Sittable(Object):

    # def at_object_creation(self):
    #     self.cmdset.add_default(CmdSetSit)

    def do_sit(self, sitter):
        '''
        Called when trying to sit on/in this object
        
        Args:
            sitter (Object): the one trying to sit down.
        '''
        preposition = self.db.preposition or "on"
        current = self.db.sitter
        if current:
            if current == sitter:
                sitter.msg(f"You are already sitting {preposition} {self.key}.")
            else:
                sitter.msg(f"You can't sit {preposition} {self.key} "
                        f"- {current.key} is already sitting there!")
            return
        self.db.sitter = sitter
        sitter.db.is_sitting = self
        #custom message
        msg = self.db.msg_sitting_down or f"You sit {preposition} {self.key}"
        sitter.msg(msg) 

    def do_stand(self, stander):
        '''
        Called when trying to stand from this object.
        
        Args:
            stander (Object): The one trying to stand up.
        '''
        current = self.db.sitter
        if not stander == current:
            stander.msg(f"You are not sitting self.db.preposition {self.key}.")
        else:
            self.db.sitter = None
            del stander.db.is_sitting
            stander.msg(f"You stand up from {self.key}.")