
@plugin
class Ping(object):
    def __init__(self, server):
        self.server = server
        self.commands = [ "ping" ]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
    
    def handle_command(self, channel, user, cmd, args):
        if cmd == "ping":
            if len(args) > 0:
                self.server.doMessage(channel, user+": Pong "+" ".join(args))
            else:
                self.server.doMessage(channel, user+": Pong")
