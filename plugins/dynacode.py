import sys

@plugin
class DynaCode(object):
    def __init__(self, server):
        self.server = server
        self.commands = [ "py" ]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
        self.env = { }
    
    def handle_command(self, channel, user, cmd, args):
        if self.server.plugins["Auth"].isOwner(user) and cmd == "py":
            if len(args) < 1:
                self.server.doMessage(channel, user+": Not enough arguments.")
                return
            
            backup = sys.stdout
            myout = OutputBuffer()
            sys.stdout = myout
            try:
                exec " ".join(args)
            except Exception,e:
                sys.stdout = backup
                self.server.doMessage(channel, user+": "+e.__class__.__name__+": "+e.__str__())
                
            sys.stdout = backup
            for line in myout.getOutput():
                self.server.doMessage(channel, user+": "+line)

class OutputBuffer(object):
    def __init__(self):
        self.__output = []
    
    def write(self, s):
        if s != "\n":
            self.__output.append(s)
    
    def getOutput(self):
        return self.__output
