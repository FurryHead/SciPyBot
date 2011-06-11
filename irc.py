import socket, os
import plugins

class PluginManager(object):
    def __init__(self, server):
        self.server = server
        self.plugins = { }
        self.handlers = { 
            "join" : [ ],
            "part" : [ ],
            "quit" : [ ],
            "message" : [ ],
            "connect" : [ ],
            "disconnect": [ ],
            "action" : [ ],
            "nick" : [ ],
            "mode" : [ ],
            "ping" : [ ],
            "command" : { },
        }
    
    def handle(self, event, handler_func, handler_commands=None):
        if event == "command":
            if handler_commands is not None:
                for command in handler_commands:
                    self.handlers["command"][command] = handler_func
        else:
            self.handlers[event].append(handler_func)
    
    def unhandle(self, event, handler_func, handler_commands=None):
        if event == "command":
            handlers = {}
            for command, handler in self.handlers[event]:
                if handler != handler_func and not command in handler_commands:
                    handlers.insert(0, handler)
                    
            self.handlers[event] = handlers
        else:
            handlers = []
            for handler in self.handlers[event]:
                if handler != handler_func:
                    handlers.insert(0, handler)
                    
            self.handlers[event] = handlers
        
    def event(self, eventName, *args):
        if eventName == "command":
            handler = None
            try:
                handler = self.handlers[eventName][args[2]]
                handler(*args)
            except KeyError,ke: pass
            except Exception, e:
                s = handler.__self__
                print("Plugin "+s.__class__.__name__+" "+e.__class__.__name__+": "+e.__str__())
        else:
            for handler in self.handlers[eventName]:
                try:
                    handler(*args)
                except KeyError: pass
                except Exception, e:
                    s = handler.__self__
                    print("Plugin "+s.__class__.__name__+" "+e.__class__.__name__+": "+e.__str__())
    
    def loadedPlugin(self, pluginName):
        return pluginName.lower() in self.plugins
    
    def pluginExists(self, pluginName):
        return plugins.getPlugin(pluginName.lower()) is not None
        
    def loadPlugin(self, pluginName):
        plugins.refresh()
        if not self.loadedPlugin(pluginName.lower()):
            if not self.pluginExists(pluginName.lower()):
                err = "No such plugin."
                return err
            
            pClass = None
            try:
                pClass = plugins.getPlugin(pluginName.lower())
            except Exception, e:
                err = "Cannot load plugin "+pluginName+" ("+e.__class__.__name__+": "+e.__str__()+")"
                print(err)
                return err
            
            try:
                self.plugins[pluginName.lower()] = pClass(self.server)
            except Exception, e:
                err = "Could not initialize "+pluginName+" ("+e.__class__.__name__+": "+e.__str__()+")"
                print(err)
                return err
                
        else:
            err = "Module has already been loaded."
            return err
    
    def getPlugin(self, pluginName): 
        try:
            return self.plugins[pluginName.lower()]
        except KeyError:
            return None
    
    def reloadPlugin(self, pluginName):
        errs = {}
        
        err = self.unloadPlugin(pluginName.lower())
        if err is not None: 
            errs["unload"] = err
            
        err = self.loadPlugin(pluginName.lower())
        if err is not None: 
            errs["load"] = err
        
        return errs
    
    def unloadPlugin(self, pluginName):
        if self.loadedPlugin(pluginName.lower()):
            inst = self.plugins[pluginName.lower()]
            for event, eList in self.handlers.items():
                if event == "command":
                    for cmd,func in eList.items():
                        if func.__self__ == inst:
                            del eList[cmd]
                            inst.__del__()
                else:
                    for func in eList[:]:
                        if func.__self__ == inst:
                            eList.remove(func)
                            inst.__del__()
                            
            del self.plugins[pluginName.lower()]
        else:
            err = "Plugin "+pluginName+" is not loaded."
            return err
    
    def loadAllPlugins(self):
        errs = {}
        for plugin in self.server.config["start_plugins"]:
            err = self.loadPlugin(plugin.lower())
            if err is not None:
                errs[plugin] = err
                
        return errs
    
    def unloadAllPlugins(self):
        errs = {}
        for plugin in self.plugins:
            err = self.unloadPlugin(plugin.lower())
            if err is not None:
                errs[plugin] = err
            
        return errs

class IRC(object):
    def __init__(self, config):
        self.pluginManager = PluginManager(self)
        self.config = config
        self.handle = self.pluginManager.handle
        self.unhandle = self.pluginManager.unhandle
        self.handlers = self.pluginManager.handlers
        self.plugins = self.pluginManager.plugins
        self.getPlugin = self.pluginManager.getPlugin
        self.pluginManager.loadAllPlugins()
        self.running = False
        
    def _readline(self):
        ret = []
        while True:
            c = self.conn.recv(1)
            if c == '\n':
                break
            else:
                if c != '\r':
                    ret.append(c)
        return "".join(ret)
           
    def connect(self):
        self.conn = socket.socket()
        self.conn.settimeout(60)
        self.conn.connect((self.config["host"], self.config["port"]))
        self.sendLine("USER "+self.config["ident"]+" * * *")
        self.sendLine("NICK "+self.config["nickname"])
        
        self.running = True
        while self.running:
            try:
                data = self._readline()
            except socket.timeout:
                self.sendLine("PING BACK")
                try:
                    data = self._readline()
                    continue
                except socket.timeout:
                    raise IOError("Connection was broken?")
          
            words = data.split(" ")
            
            if words[0] == "PING":
                # The server pinged us, we need to pong or we'll be disconnected
                # (make sure to send whatever follows the PING, in case they send a random hash)
                self.sendLine("PONG " + data[5:])
                continue
            
            # Takes the ':Nick!Ident@Host' chunk and assigns Nick to user
            user = words[0].split(":")[1].split("!")[0]
            
            #TODO: Add code for handling nick collisions
            
            if words[1] == "376":
                # We successfully logged in, do post-login procedures
                if self.config["loginname"] is not None and self.config["loginpass"] is not None:
                    self.doMessage("NickServ", "IDENTIFY "+self.config["loginname"]+" "+self.config["loginpass"])
                
                self.pluginManager.event("connect", self.config["host"])
                
                for chan in self.config["start_channels"]:
                    self.doJoin(chan)
            
            elif words[1] == "PRIVMSG":
                # We got a message
                channel = words[2]
                message = data[data.find(":", data.find(channel[(channel.find("-") == -1 and 1 or channel.find("-")):]))+1:]
                if message.find("\x01ACTION") == 0:
                    # String was found, it's an action
                    self.pluginManager.event("action", channel, user, message[8:-1])
                elif message.find(self.config["cmdPrefix"]) == 0:
                    # String was found, it's a command!
                    args = message.split(" ")
                    cmd = args[0][len(self.config["cmdPrefix"]):]
                    args.pop(0)
                    self.pluginManager.event("message", channel, user, message)
                    self.pluginManager.event("command", channel, user, cmd, args)
                else:
                    # Strings not found, it's a message
                    self.pluginManager.event("message", channel, user, message)
            
            elif words[1] == "JOIN":
                # Someone joined a channel that we're in
                if user != self.config["nickname"]:
                    self.pluginManager.event("join", words[2][1:], user)
            
            elif words[1] == "PART":
                if user != self.config["nickname"]:
                    # Someone parted a channel we're in
                    self.pluginManager.event("part", words[2], user, " ".join(words[3:]))
            
            elif words[1] == "QUIT":
                # Someone quit the server
                self.pluginManager.event("quit", user, " ".join(words[2:])[1:]) 
            
            elif words[1] == "NICK":
                # Someone changed their nickname 
                self.pluginManager.event("nick", user, words[2][1:])
            
            elif words[1] == "MODE":
                # Someone set a mode
                try:
                    self.pluginManager.event("mode", words[2], user, words[3], words[4])
                except IndexError: # words[4] is not valid, it wasn't set on a user
                    self.pluginManager.event("mode", words[2], user, words[3], "")
        
        #end of loop
        self.pluginManager.event("disconnect", self.config["host"])
        
    def sendLine(self, line):
        self.conn.send(line+"\r\n")
    
    def doMessage(self, channel, message):
        self.sendLine("PRIVMSG "+channel+" :"+message)
        self.pluginManager.event("message", channel, self.config["nickname"], message)
        
    def doAction(self, channel, action):
        self.sendLine("PRIVMSG "+channel+" :\x01ACTION "+action+" \x01")
        self.pluginManager.event("action", channel, self.config["nickname"], action)
    
    def doQuit(self, message=None):
        self.sendLine("QUIT " + (message or ""))
        self.pluginManager.event("quit", self.config["nickname"], (message or ""))
        self.running = False
    
    def doNotice(self, user, message):
        self.sendLine("NOTICE "+user+" :"+message)
    
    def doNick(self, newnick):
        self.sendLine("NICK " + newnick)
        self.pluginManager.event("nick", self.config["nickname"], newnick)
        self.config["nickname"] = newnick
    
    def doJoin(self, channel):
        self.sendLine("JOIN "+channel)
        self.pluginManager.event("join", channel, self.config["nickname"])
        
    def doPart(self, channel, message=None):
        self.sendLine("PART "+channel)
        self.pluginManager.event("part", self.config["nickname"], (message or ""))
    
    def doMode(self, channel, mode, user=None):
        self.sendLine("MODE "+channel+" "+mode+(user if user is not None else ""))
        self.pluginManager.event("mode", channel, self.config["nickname"], mode, (user if user is not None else ""))

cfg = {
    "host" : "irc.freenode.net",
    "port" : 6667,
    "nickname" : "SciPyBot",
    "ident" : "SciPyBot",
    "loginname" : None,
    "loginpass" : None,
    "start_channels" : [ "#guppy"],
    "start_plugins" : ["Printer", "PluginLoader"],
    "cmdPrefix" : "+"
}
irc = IRC(cfg)
irc.connect()
