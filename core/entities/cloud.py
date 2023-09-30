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

x,y,z = var_position
i = randint(-1,1) + x
j = randint(-1,1) + y
k = randint(-1,1) + z
r = randint(3,13)
var_cango = True
block = chr(0)
try:
    world[x, y, z] = block
except:
    world[x, y, z] = block
self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
self.client.sendBlock(x, y, z, block)
self.client.queueTask(TASK_BLOCKSET, (x-1, y, z, block), world=world)
self.client.sendBlock(x-1, y, z, block)
self.client.queueTask(TASK_BLOCKSET, (x+1, y, z, block), world=world)
self.client.sendBlock(x+1, y, z, block)
self.client.queueTask(TASK_BLOCKSET, (x, y, z-1, block), world=world)
self.client.sendBlock(x, y, z-1, block)
self.client.queueTask(TASK_BLOCKSET, (x, y, z+1, block), world=world)
self.client.sendBlock(x, y, z+1, block) 
try:
    #if self.runonce == None:
    #    self.runonce = 0
    #    entity[4] = x
    #    entity[5] = y
    #    entity[6] = z
    #dx = abs(x - entity[4])
    #dy = abs(y - entity[5])
    #dz = abs(z - entity[6])
    #print(dy)
    #if entity[4] + 6 < dx or entity[5] + 6 < dy or entity[6] + 6 < dz:
    #    var_cango = False
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i, j, k)])
    if blocktocheck != 0:
        var_cango = False
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i-1, j, k)])
    if blocktocheck != 0:
        var_cango = False
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i+1, j, k)])
    if blocktocheck != 0:
        var_cango = False
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i, j, k-1)])
    if blocktocheck != 0:
        var_cango = False
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i, j, k+1)])
    if blocktocheck != 0:
        var_cango = False
except:
    var_cango = False
if var_cango and randint(0,2) != 2:
    var_position = (i,j,k)
    x,y,z = var_position
    block = chr(36) 
    try:
        world[x, y, z] = block
    except:
        world[x, y, z] = block
    self.client.queueTask(TASK_BLOCKSET, (x, y, z, block), world=world)
    self.client.sendBlock(x, y, z, block)
    self.client.queueTask(TASK_BLOCKSET, (x-1, y, z, block), world=world)
    self.client.sendBlock(x-1, y, z, block)
    self.client.queueTask(TASK_BLOCKSET, (x+1, y, z, block), world=world)
    self.client.sendBlock(x+1, y, z, block)
    self.client.queueTask(TASK_BLOCKSET, (x, y, z-1, block), world=world)
    self.client.sendBlock(x, y, z-1, block)
    self.client.queueTask(TASK_BLOCKSET, (x, y, z+1, block), world=world)
    self.client.sendBlock(x, y, z+1, block)
    blocktocheck = ord(world.blockstore.raw_blocks[world.blockstore.get_offset(i, j-1, k)])
    if blocktocheck == 0 and randint(-1,2) == 0:
        entitylist.append(["rain",(x,y-1,z),r,r])
else:
    entitylist.append(["rain",(x,y-1,z),r,r])
