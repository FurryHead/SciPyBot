
@plugin
class Die(object):
    def __init__(self, server):
        self.server = server
        self.server.pluginManager.loadPlugin("Auth")
        self.commands = [ "die" ]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
    
    def handle_command(self, channel, user, cmd, args):
        if self.server.getPlugin("auth").isOwner(user):
            self.server.doMessage(channel, self.server.getPlugin("auth").owner + " wants me to leave, but I'll be back!")
            self.server.doQuit()
