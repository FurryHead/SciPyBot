
@plugin
class ChannelTools(object):
    def __init__(self, server):
        self.server = server
        self.commands = [ "join", "part" ]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
        
    def handle_command(self, channel, user, cmd, args):
        if self.server.getPlugin("auth").isMod(user):
            if len(args) < 1:
                self.server.doMessage(channel, user+": Not enough arguments.")
                return
            
            if cmd == "join":
                self.server.doJoin(args[0])
            elif cmd == "part":
                self.server.doPart(args[0])
