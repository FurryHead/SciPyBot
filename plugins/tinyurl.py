import urllib

@plugin
class TinyURL(object):
    def __init__(self, server):
        self.server = server
        self.commands = ["tinyurl"]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
    
    def handle_command(self, channel, user, cmd, args):
        if cmd == "tinyurl":
            if len(args) < 1:
                self.server.doMessage(channel, user+": Not enough arguments.")
                return
            
            url = args[0] if args[0].startswith("http://") else "http://"+args[0]
            self.server.doMessage(channel, user+": "+urllib.urlopen("http://tinyurl.com/api-create.php?url="+url).readline())
