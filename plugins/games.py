import random

UNODECK = ['b0', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8', 'b9', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8', 'g9', 'y0', 'y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9', 'y1', 'y2', 'y3', 'y4', 'y5', 'y6', 'y7', 'y8', 'y9', 'r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9', 'rS', 'gS', 'bS', 'yS', 'rD2', 'gD2', 'bD2', 'yD2', 'rR', 'gR', 'bR', 'yR', 'wW', 'wW', 'wW', 'wW', 'wWD4', 'wWD4', 'wWD4', 'wWD4', 'rS', 'gS', 'bS', 'yS', 'rD2', 'gD2', 'bD2', 'yD2', 'rR', 'gR', 'bR', 'yR']

@plugin 
class Uno(object):
    def __init__(self, server):
        self.server = server
        self.commands = []
        self.server.handle("command", getattr(self, "handle_command"), self.commands)
    
    def handle_command(self, channel, user, cmd, args):
        pass
    
