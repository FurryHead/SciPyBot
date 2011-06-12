import os, re

@plugin
class Info(object):
    def __init__(self, server):
        self.server = server
        self.commands = [ "what", "learn", "forget", "fulldb" ]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
        self.server.handle("message", getattr(self, "handle_message"))
        self.dbfile = "plugins/info.db"
        self.infodb = {}
        self.validchars = re.compile("[^A-Za-z0-9_-]")
        
        if os.path.isfile(self.dbfile):
            fh = open(self.dbfile, "r")
            for line in fh.read().split("\n"):
                if line == "": continue
                k,v = line.split("\t")
                self.infodb[k] = v
    
    def __del__(self):
        fh = open(self.dbfile+".tmp", "w")
        for k,v in self.infodb.items():
            fh.write("%s\t%s\n" % (k,v))
        fh.close()
        os.rename(self.dbfile+".tmp", self.dbfile)
    
    def getInfo(self, key):
        for k,v in self.infodb.items():
            if k.lower() == key.lower():
                return k,v 
        
        return None, None
        
    def handle_command(self, channel, user, cmd, args, info_silent = False):
        if cmd == "what":
            for i in range(0, len(args)):
                args[i] = self.validchars.sub("", args[i])
        
            ind = 0
            for i in range(0, len(args)):
                if args[i] == "is" or args[i] == "are" or args[i] == "a" or args[i] == "an" or args[i] == "":
                    ind += 1
                else:
                    break
            
            nargs = []
            for i in range(ind, len(args)):
                if args[i] != "":
                    nargs.append(args[i])
                
            args = nargs
            
            if len(args) < 1:
                if not info_silent:
                    self.server.doMessage(channel, "...what should I tell you about?")
                return

            tmp = " ".join(args)
            k,v = self.getInfo(tmp)

            if k is not None and v is not None:
                self.server.doMessage(channel, user + ": " + k + ": " + v)
            else:
                if not info_silent:
                    self.server.doMessage(channel, user + ", I don't know what " + tmp + " is.")
                    
        elif self.server.getPlugin("auth").isMod(user):
            if cmd == "learn":
                if len(args) < 1:
                    self.server.doMessage(channel, "...what should I learn?")
                    return
                
                tmp = " ".join(args)
                ind = tmp.find(" as ")
                size = 4
                if ind == -1: 
                    ind = tmp.find(" as: ")
                    size = 5
                    if ind == -1:
                        self.server.doMessage(channel, "...what should I learn " + tmp + " as?")
                        return
                        
                val = tmp[ind+size:]
                key = tmp[0:ind]
                key = key.replace("\t", "")
                k,v = self.getInfo(key) 
                if k is not None and v is not None:
                    self.server.doMessage(channel, "I already know what " + k + " is.")
                    return
                    
                self.infodb[key] = val
                self.server.doMessage(channel, "Ok, I learned what " + key + " is.")
            elif cmd == "forget":
                if len(args) < 1:
                    self.server.doMessage(channel, "...what should I forget?")
                    return
                    
                key = ""
                tmp = " ".join(args)
                if tmp[:-1] == " ": tmp.pop()
                for k,v in self.infodb.items():
                    if k.lower() == tmp.lower():
                        del self.infodb[k]
                        key = k
                        
                if key != "":
                    self.server.doMessage(channel, "Hmm, I can't seem to remember what "+key+" is anymore.")
                else:
                    self.server.doMessage(channel, "I don't know what "+tmp+" is.")
            elif cmd == "fulldb":
                self.server.doMessage(channel, user+": My database contains (separated by '#'): "+" # ".join(self.infodb.keys()))
    
    def handle_message(self, channel, user, message):
        if message.lower().startswith("what"):
            args = message.split(" ")[1:]
            self.handle_command(channel, user, "what", args, True)
