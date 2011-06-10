import random

@plugin 
class Smack(object):
    def __init__(self, server):
        self.server = server
        self.commands = [ "smack" ]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
        self.objects = [ "smelly fish",
                                  "tin pot",
                                  "frying pan",
                                  "mouse",
                                  "keyboard",
                                  "fly swatter"
                                  ]
    
    def handle_command(self, channel, user, cmd, args):
        if cmd == "smack" and len(args) > 0:
            self.server.doAction(channel, "smacks "+args[0]+" with a "+self.objects[random.Random().randint(0, len(self.objects)-1)]+"!")
    
