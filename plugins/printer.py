
@plugin
class Printer(object):
    def __init__(self, server):
        self.server = server
        for h in self.server.handlers:
            func = getattr(self, "handle_"+h, None)
            if func is not None:
                self.server.handle(h, func)
    
    def handle_connect(self, server):
        print("I have connected to %s" % server)
    
    def handle_disconnect(self, server):
        print("I have disconnected from %s" % server)
    
    def handle_message(self, channel, user, message):
        print("<%s> %s: %s" % (channel, user, message))
    
    def handle_action(self, channel, user, action):
        print("<%s> * %s %s" % (channel, user, action))
    
    def handle_join(self, channel, user):
        print("%s has joined %s" % (user, channel))
        
    def handle_part(self, channel, user, message):
        print("%s has left %s (%s)" % (user, channel, message))
        
    def handle_quit(self, user, message):
        print("%s has quit (%s)" % (user, message))
    
    def handle_nick(self, oldnick, newnick):
        print("%s is now known as %s" % (oldnick, newnick))
    
    def handle_mode(self, channel, user, mode, otheruser):
        print("%s set mode %s on %s" % (user, mode, otheruser if otheruser != "" else channel))
