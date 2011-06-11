import sys

@plugin
class PluginLoader(object):
    def __init__(self, server):
        self.server = server
        self.server.pluginManager.loadPlugin("Auth")
        self.commands = ["load", "unload", "reload", "reloadall", "loaded", "allplugins"]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
        
    def handle_command(self, channel, user, cmd, args):
        if self.server.getPlugin("auth").isMod(user):
            if cmd == "reloadall":
                self.server.pluginManager.unloadAllPlugins()
                errs = self.server.pluginManager.loadAllPlugins()
                if errs: 
                    errStr = ""
                    for k,v in errs:
                        errStr += "Plugin "+k+": "+v+" ----- "
                    self.server.doMessage(channel, user+": Exceptions occurred with the following plugins: "+errStr)
                return 
            elif cmd == "allplugins":
                self.server.doMessage(channel, user+": Available plugins: "+" ".join(sys.modules["__main__"].plugins.pList.keys()))
                return
                
            if len(args) < 1:
                self.server.doMessage(channel, user+": Not enough arguments.")
                return
            
            if cmd == "load":
                err = self.server.pluginManager.loadPlugin(args[0])
                if err is not None:
                    if err == "Module has already been loaded.":
                        self.server.doMessage(channel, user+": Plugin "+args[0]+" has already been loaded.")
                    else:
                        self.server.doMessage(channel, user+": Exception loading plugin "+args[0]+": "+err)
                else:
                    self.server.doMessage(channel, user+": Successfully loaded plugin "+args[0]+".")
            elif cmd == "unload":
                if args[0] == self.__module__+"."+self.__class__.__name__:
                    self.server.doMessage(channel, user+": You can't unload the plugin loader front-end. (You can reload it, though!)")
                    return
                
                err = self.server.pluginManager.unloadPlugin(args[0])
                if err is not None:
                    if err == "Plugin "+args[0]+" is not loaded.":
                        self.server.doMessage(channel, user+": Plugin "+args[0]+" has not been loaded.")
                    else:
                        self.server.doMessage(channel, user+": Exception unloading plugin "+args[0]+": "+err)
                else:
                    self.server.doMessage(channel, user+": Successfully unloaded plugin "+args[0]+".")
            elif cmd == "reload":
                err = self.server.pluginManager.reloadPlugin(args[0])
                if err is not None and err:
                    self.server.doMessage(channel, user+": Exception reloading plugin "+args[0]+": "+" ".join([v for k,v in err.items()]))
                else:
                    self.server.doMessage(channel, user+": Successfully reloaded plugin "+args[0]+".")
            elif cmd == "loaded":
                if self.server.pluginManager.loadedPlugin(args[0]):
                    self.server.doMessage(channel, user+": Plugin "+args[0]+" is loaded.")
                else:
                    if self.server.pluginManager.pluginExists(args[0]):
                        self.server.doMessage(channel, user+": Plugin "+args[0]+" is not loaded.")
                    else:
                        self.server.doMessage(channel, user+": Plugin "+args[0]+" does not exist.")
