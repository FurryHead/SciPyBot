import os, inspect, collections

pList = { }
mList = collections.defaultdict(list)

class NoSuchPluginError(Exception): pass

def plugin(cls):
    #Using inspect, figure out what file is calling this function (using @plugin)
    clsFile = inspect.stack()[1][1]
    
    #Split the path, because it will be in the form "plugins" + os.sep + "*.py"
    modFile = clsFile.split(os.sep)[1]
    
    #Append the class name to the list indexed by module file name
    mList[modFile].append(cls.__name__.lower())
    
    #Set class (plugin) name to the class (plugin) reference
    pList[cls.__name__.lower()] = cls
    
    #return cls, since decorators must return the "new" type
    return cls

def refresh(pluginName = None):
    """
    Refreshes the list of module/class pairs, and plugin/class pairs.
    
    If pluginName is not None, it can raise NoSuchPluginError.
    Regardless of the value of pluginName, it can raise any error a python file can raise, samme as using import.
    """
    
    #if we are asked to do a general refresh of list
    if pluginName is None:
        #we were asked to refresh, so clear out our lists so we can start fresh
        pList.clear()
        mList.clear()
        
        #load every module in the plugins package
        _files = [os.path.join("plugins", f) for f in os.listdir("plugins") if f != "__init__.py" and f.endswith(".py") and not os.path.isdir(os.path.join("plugins",f))]
        
        #for file (module) in the file list
        for f in _files:
            #Set "plugin" in the environment so that @plugin decorators work correctly
            env = {"plugin":plugin}
            
            #Execute the file. The file will automatically update the list of plugins, due to the @plugin decorator
            execfile(f, env, env)
    else:
        #We're trying to refresh a module, so use _reload instead.
        found = __reload(pluginName)
        #if it wasn't found, try refreshing all modules and try again
        if not found:
            refresh()
            found = __reload(pluginName)
            
            #if it's still not found, raise an error.
            if not found: 
                raise NoSuchPluginError()


def __reload(pluginName):
    #iterate over each "file", "module" pair in mList
    for f,classes in mList:
        #if the requested
        if pluginName in classes:
            #Set "plugin" in the environment so that @plugin decorators work correctly
            env = {"plugin":plugin}
            
            #Execute the file. The file will automatically update the list of plugins, due to the @plugin decorator
            execfile(f, env, env)
            
            #return True, indicating we have found and reloaded the module.
            return True
    
    #Else, we have not found it, so return False.
    return False

def getPlugin(name):
    """ Helper function to get a plugin's class. """
    try:
        return pList[name.lower()]
    except KeyError:
        return None

refresh()
