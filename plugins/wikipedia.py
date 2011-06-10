import urllib
from xml.dom import minidom

@plugin
class Wikipedia(object):
    def __init__(self, server):
        self.server = server
        self.commands = ["wiki"]
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
    
    def handle_command(self, channel, user, cmd, args):
        if cmd == "wiki":
            if len(args) < 1: 
                self.server.doMessage(channel, user+": What should I search for on Wikipedia?")
                return
            
            url = "http://en.wikipedia.org/w/api.php?action=opensearch&limit=3&namespace=0&format=xml&search="
            query = " ".join(args)
            search = url + urllib.quote_plus(query, "/")
            
            try:
                data = urllib.urlopen(search).readlines()
            except IOError, ioe:
                self.server.doMessage(channel, user+": I/O Error retrieving the results: "+ioe)
                return
            
            print data[0]
            xmldoc = minidom.parseString(data[0]) 
            searchResults = xmldoc.childNodes[0].childNodes[1].childNodes
            for result in searchResults:
                resultStr = ""
                for item in result.childNodes:
                    for textNode in item.childNodes:
                        resultStr += textNode.data + " - "
                    
                self.server.doMessage(channel, user+": "+resultStr)
