import os

@plugin
class Auth(object):
    def __init__(self, server):
        self.server = server
        self.commands = [ "addadmin", "addmod", "deladmin", "delmod", "admins", "mods", "owner", "owners" ]
        self.owner = "FurryHead"
        self.admins = []
        self.mods = []
        self.server.handle("command", self.handle_command, self.commands)
        
    def handle_command(self, channel, user, cmd, args):
        if cmd == "owner" or cmd == "owners":
            self.server.doMessage(channel, user+": My owner is "+self.owner)
        elif cmd == "admins":
            self.server.doMessage(channel, user+": My administrators are: "+" ".join(self.admins))
        elif cmd == "mods":
            self.server.doMessage(channel, user+": My moderators are: "+" ".join(self.mods))
            
        elif self.isOwner(user):
            if len(args) < 1:
                self.server.doMessage(channel, user+": Not enough arguments.")
                return
            
            if cmd == "addadmin":
                if args[0] in self.admins: return
                self.admins.append(args[0])
            elif cmd == "addmod":
                if args[0] in self.mods: return
                self.mods.append(args[0])
            elif cmd == "deladmin":
                if args[0] in self.admins:
                    self.admins.remove(args[0])
            elif cmd == "delmod":
                if args[0] in self.mods:
                    self.mods.remove(args[0])
    
    def _loadusers(self):
        try:
            fh = open("./plugins/auth.users", "r")
        except IOError:
            pass

        for line in fh.readlines():
            if line == "": return
            tmp = line.split("\t")
            tads = tmp[0].split(" ")
            if tads != "":
                admins = tads[:]
                
            tmds = tmp[1].split(" ")
            if len(tmds) <= 1 and tmds[0] != "":
                mods = tmds[:]
        
        fh.close()
    
    def _saveusers(self):
        fh = open("./plugins/auth.users.tmp", "w")
        if len(self.admins) >= 1:
            for admin in self.admins:
                fh.write(" "+admin)
                
        else:
            fh.write(" ")
            
        fh.write("\t")
        
        if len(self.mods) >= 1:
            for mod in self.mods:
                fh.write(mod+" ")

        else:
            fh.write(" ")

        fh.close()
        os.rename("./plugins/auth.users.tmp", "./plugins/auth.users")
    
    def isOwner(self, user):
        return user == self.owner
    
    def isAdmin(self, user):
        if user in self.admins: 
            return True
        else:
            return user == self.owner
    
    def isMod(self, user):
        if user in self.mods: 
            return True
        elif user in self.admins: 
            return True
        else:
            return user == self.owner
