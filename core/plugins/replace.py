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

class BrepPlugin(ProtocolPlugin):
    
    commands = {
        "replace": "commandBrep",
        "brep": "commandBrep",
        "creplace": "commandCreplace",
        "crep": "commandCreplace",
        "fill": "commandFill",
    }
    
    @build_list
    @builder_only
    def commandBrep(self, parts, byuser, overriderank):
        "/replace blockA blockB [x y z x2 y2 z2] - Builder\nAliases: brep\nReplaces all blocks of blockA in this area to blockB."
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendServerMessage("Please enter types (and possibly two coord triples)")
        else:
            blockA = self.client.GetBlockValue(parts[1])
            if blockA == None:
                return
            # Try getting the block as a direct integer type.
            blockB = self.client.GetBlockValue(parts[2])
            if blockB == None:
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
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
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            if self.client.isDirector() or overriderank:
                limit = self.client.factory.build_director
            elif self.client.isAdmin():
                limit = self.client.factory.build_admin
            elif self.client.isMod():
                limit = self.client.factory.build_mod
            elif self.client.isOp():
                limit = self.client.factory.build_op
            else:
                limit = self.client.factory.build_other
            # Stop them doing silly things
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to replace.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for i in range(x, x2+1):
                    for j in range(y, y2+1):
                        for k in range(z, z2+1):
                            if not self.client.AllowedToBuild(i, j, k) and byuser==False:
                                return
                            try:
                                check_offset = world.blockstore.get_offset(i, j, k)
                                block = world.blockstore.raw_blocks[check_offset]
                                if block == blockA:
                                    world[i, j, k] = blockB
                                    self.client.runHook("blockchange", x, y, z, ord(block), ord(block), byuser)
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, blockB), world=world)
                                    self.client.sendBlock(i, j, k, blockB)
                            except AssertionError:
                                self.client.sendServerMessage("Out of bounds replace error.")
                                return
                            yield
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10):
                        next(block_iter)
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if byuser:
                        self.client.sendServerMessage("Your replace just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandCreplace(self, parts, byuser, overriderank):
        "/creplace typeA typeB typeC [x y z x2 y2 z2] - Op\nAliases: crep\nReplaces all blocks of typeA in this cuboid to typeB and typeC."
        if len(parts) < 10 and len(parts) != 4:
            self.client.sendServerMessage("Please enter the type to replace and two other types")
            self.client.sendServerMessage("(and possibly two coord triples)")
        else:
            # Try getting the block as a direct integer type.
            try:
                blockA = chr(int(parts[1]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    blockA = chr(globals()['BLOCK_%s' % parts[1].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                    return
            # Check the block is valid
            if ord(blockA) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            # Try getting the block as a direct integer type.
            try:
                blockB = chr(int(parts[2]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    blockB = chr(globals()['BLOCK_%s' % parts[2].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[2])
                    return
            # Try getting the block as a direct integer type.
            try:
                blockC = chr(int(parts[3]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    blockC = chr(globals()['BLOCK_%s' % parts[3].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[3])
                    return
            # Check the block is valid
            if ord(blockB) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[2])
                return
            # Check the block is valid
            if ord(blockC) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[2])
                return
            # If they only provided the type argument, use the last two block places
            if len(parts) == 4:
                try:
                    x, y, z = self.client.last_block_changes[0]
                    x2, y2, z2 = self.client.last_block_changes[1]
                except IndexError:
                    self.client.sendServerMessage("You have not clicked two corners yet.")
                    return
            else:
                try:
                    x = int(parts[4])
                    y = int(parts[5])
                    z = int(parts[6])
                    x2 = int(parts[7])
                    y2 = int(parts[8])
                    z2 = int(parts[9])
                except ValueError:
                    self.client.sendServerMessage("All parameters must be integers")
                    return
            if x > x2:
                x, x2 = x2, x
            if y > y2:
                y, y2 = y2, y
            if z > z2:
                z, z2 = z2, z
            if self.client.isDirector() or overriderank:
                limit = self.client.factory.build_director
            elif self.client.isAdmin():
                limit = self.client.factory.build_admin
            elif self.client.isMod():
                limit = self.client.factory.build_mod
            elif self.client.isOp():
                limit = self.client.factory.build_op
            else:
                limit = self.client.factory.build_other
            # Stop them doing silly things
            if (x2 - x) * (y2 - y) * (z2 - z) > limit:
                self.client.sendServerMessage("Sorry, that area is too big for you to rep.")
                return
            # Draw all the blocks on, I guess
            # We use a generator so we can slowly release the blocks
            # We also keep world as a local so they can't change worlds and affect the new one
            world = self.client.world
            def generate_changes():
                for i in range(x, x2+1):
                    for j in range(y, y2+1):
                        for k in range(z, z2+1):
                            try:
                                blockcheck = world.blockstore.raw_blocks[world.blockstore.get_offset(i, j, k)]
                                if blockcheck == blockA:
                                    if (i+j+k)%2 == 0:
                                        var_block = blockB
                                    else:
                                        var_block = blockC
                                    world[i, j, k] = var_block
                                    self.client.queueTask(TASK_BLOCKSET, (i, j, k, var_block), world=world)
                                    self.client.sendBlock(i, j, k, var_block)
                            except AssertionError:
                                self.client.sendServerMessage("Out of bounds creplace error.")
                                return
                            yield
            # Now, set up a loop delayed by the reactor
            block_iter = iter(generate_changes())
            def do_step():
                # Do 10 blocks
                try:
                    for x in range(10):
                        next(block_iter)
                    reactor.callLater(0.01, do_step)
                except StopIteration:
                    if byuser:
                        self.client.sendServerMessage("Your creplace just completed.")
                    pass
            do_step()

    @build_list
    @op_only
    def commandFill(self, parts, byuser, overriderank):
        "/fill blockname repblock [x y z x2 y2 z2] - Op\nFills the area with the block."
        if len(parts) < 9 and len(parts) != 3:
            self.client.sendSplitServerMessage("Please enter a type and a type to replace (and possibly two coord triples)")
            self.client.sendSplitServerMessage("Note that you must place two blocks to use it. The first block sets where to spread from and the second block sets which directions to spread.")
        else:
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
            # Try getting the repblock as a direct integer type.
            try:
                var_repblock = chr(int(parts[2]))
            except ValueError:
                # OK, try a symbolic type.
                try:
                    var_repblock = chr(globals()['BLOCK_%s' % parts[2].upper()])
                except KeyError:
                    self.client.sendServerMessage("'%s' is not a valid block type." % parts[2])
                    return
            # Check the block is valid
            if ord(block) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[1])
                return
            # Check the repblock is valid
            if ord(var_repblock) > 49:
                self.client.sendServerMessage("'%s' is not a valid block type." % parts[2])
                return
            # If they only provided the type argument, use the last block place
            if len(parts) == 3:
                try:
                    x, y, z = self.client.last_block_changes[1]
                    x2, y2, z2 = self.client.last_block_changes[0]
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
                limit = self.client.factory.build_director
            elif self.client.isAdmin():
                limit = self.client.factory.build_admin
            elif self.client.isMod():
                limit = self.client.factory.build_mod
            elif self.client.isOp():
                limit = self.client.factory.build_op
            else:
                limit = self.client.factory.build_other
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
                        self.client.sendServerMessage("You have exceeded the fill limit for your rank.")
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
                    for x in range(10): # 10 blocks at a time, 10 blocks per tenths of a second, 100 blocks a second
                        next(block_iter)
                    reactor.callLater(0.01, do_step) # This is how long (in seconds) it waits to run another 10 blocks
                except StopIteration:
                    if byuser:
                        self.client.sendServerMessage("Your fill just completed.")
                    pass
            do_step()
