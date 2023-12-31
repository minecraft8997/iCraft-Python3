#    iCraft is Copyright 2010-2011 both
#
#    The Archives team:
#                   <Adam Guy> adam@adam-guy.com AKA "Adam01"
#                   <Andrew Godwin> andrew@aeracode.org AKA "Aera"
#                   <Dylan Lukes> lukes.dylan@gmail.com AKA "revenant"
#                   <Gareth Coles> colesgareth2@hotmail.com AKA "gdude2002"
#
#    And,
#
#    The iCraft team:
#                   <Andrew Caluzzi> tehcid@gmail.com AKA "tehcid"
#                   <Andrew Dolgov> fox@bah.org.ru AKA "gothfox"
#                   <Andrew Horn> Andrew@GJOCommunity.com AKA "AndrewPH"
#                   <Brad Reardon> brad@bradness.co.cc AKA "PixelEater"
#                   <Clay Sweetser> CDBKJmom@aol.com AKA "Varriount"
#                   <James Kirslis> james@helplarge.com AKA "iKJames"
#                   <Jason Sayre> admin@erronjason.com AKA "erronjason"
#                   <Jonathon Dunford> sk8rjwd@yahoo.com AKA "sk8rjwd"
#                   <Joseph Connor> destroyerx100@gmail.com AKA "destroyerx1"
#                   <Kamyla Silva> supdawgyo@hotmail.com AKA "NotMeh"
#                   <Kristjan Gunnarsson> kristjang@ffsn.is AKA "eugo"
#                   <Nathan Coulombe> NathanCoulombe@hotmail.com AKA "Saanix"
#                   <Nick Tolrud> ntolrud@yahoo.com AKA "ntfwc"
#                   <Noel Benzinger> ronnygmod@gmail.com AKA "Dwarfy"
#                   <Randy Lyne> qcksilverdragon@gmail.com AKA "goober"
#                   <Willem van der Ploeg> willempieeploeg@live.nl AKA "willempiee"
#
#    Disclaimer: Parts of this code may have been contributed by the end-users.
#
#    iCraft is licensed under the Creative Commons
#    Attribution-NonCommercial-ShareAlike 3.0 Unported License. 
#    To view a copy of this license, visit http://creativecommons.org/licenses/by-nc-sa/3.0/
#    Or, send a letter to Creative Commons, 171 2nd Street,
#    Suite 300, San Francisco, California, 94105, USA.

import sys
from twisted.internet import reactor
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *

class FungisPlugin(ProtocolPlugin):
    
    commands = {
        "fungus": "commandFungus",
    }

    @build_list
    @op_only
    def commandFungus(self, parts, byuser, overriderank):
        "/fungus blockname repblock [x y z x2 y2 z2] - Op\nFunguses the area with the block."
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendSplitServerMessage("Please enter a type and a type to replace (and possibly two coord triples)")
            self.client.sendSplitServerMessage("Note that you must place two blocks to use it. The first block sets where to spread from and the second block sets which directions to spread.")
        else:
            var_repblock = chr(0)
            # Try getting the block as a direct integer type.
            try:
                block = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    block = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            # If they only provided the type argument, use the last block place
            if len(parts) == 3:
                try:
                    x = self.client.world.x /2
                    y = self.client.world.y /2
                    z = self.client.world.z /2
                    x, y, z = x, y, z
                    x2, y2, z2 = 0, 0, 0
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two points yet.")
                    return
            else:
                try:
                    x = int(parts[3])
                    y = int(parts[4])
                    z = int(parts[5])
                    x2 = int(parts[6])
                    y2 = int(parts[7])
                    z2 = int(parts[8])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            if self.client.isDirector() or overriderank:
                limit = 1073741824
            elif self.client.isAdmin():
                limit = 2097152
            elif self.client.isMod():
                limit = 262144
            elif self.client.isOp():
                limit = 110592
            elif self.client.isMember():
                limit = 55296
            else:
                limit = 4062
            var_locxchecklist = [(1,0,0),(-1,0,0)]
            var_locychecklist = [(0,1,0),(0,-1,0)]
            var_loczchecklist = [(0,0,1),(0,0,-1)]
            var_locchecklist = []
            if x != x2:
                var_locchecklist = var_locchecklist + var_locxchecklist
            if y != y2:
                var_locchecklist = var_locchecklist + var_locychecklist
            if z != z2:
                var_locchecklist = var_locchecklist + var_loczchecklist
            if var_locchecklist==[]:
                self.client.sendServerMessage("Repeated points error")
                return
            self.var_blocklist = [(x,y,z,(-20,-20,-20))]
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            try:
                if not self.client.AllowedToBuild(x, y, z):
                    self.client.sendServerMessage("You do not have permission to build here.")
                    return
                world[x, y, z] = block
                self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
                self.client.sendBlock(x, y, z, block)
            except:
                pass
            def generate_changes():
                var_blockchanges = 0
                while self.var_blocklist != []:
                    if var_blockchanges > limit:
                        self.client.sendServerMessage("You have exceeded the fungus limit for your rank.")
                        return
                    i,j,k,positionprevious = self.var_blocklist[0]
                    var_blockchanges += 1
                    for offsettuple in var_locchecklist:
                        ia,ja,ka = offsettuple
                        ri,rj,rk = i+ia,j+ja,k+ka
                        if (ri,rj,rk) != positionprevious:
                            try:
                                if not self.client.AllowedToBuild(ri,rj,rk):
                                    self.client.sendServerMessage("You do not have permission to build here.")
                                    return
                                checkblock = world.blockstore.raw_blocks[world.blockstore.get_offset(ri, rj, rk)]
                                if checkblock == var_repblock:
                                    world[ri, rj, rk] = block
                
                                    self.client.queueTask(TASK_BLOCKSET, (ri, rj, rk, block), world=world)
                                    self.client.sendBlock(ri, rj, rk, block)
                                    self.var_blocklist.append((ri, rj, rk,(i,j,k)))
                            except AssertionError:
                                pass
                            yield
                    del self.var_blocklist[0]
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(7):#10 blocks at a time, 10 blocks per tenths of a second, 100 blocks a second
                        next(block_iter)
                    reactor.callLater(0.01, do_step)  #This is how long(in seconds) it waits to run another 10 blocks
                except StopIteration:
                    if byuser:
                        self.client.sendServerMessage("Your fungus just completed.")
                    pass
            do_step()
