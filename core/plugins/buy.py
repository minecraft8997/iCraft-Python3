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

import pickle
from core.plugins import ProtocolPlugin
from core.decorators import *
from core.constants import *
from core.globals import *

class BuyPlugin(ProtocolPlugin):
    
    commands = {
        "buy": "commandBuy",
    }
    
    def commandBuy(self, parts, byuser, overriderank):
        "/buy worldname size - Guest\nMakes a new world, and boots it, if the user has enough money."
        if len(parts) == 1:
            self.client.sendServerMessage("Please specify a new worldname and size.")
        elif self.client.factory.world_exists(parts[1]):
            self.client.sendServerMessage("Worldname in use")
        else:
            if len(parts) == 3 or len(parts) == 4:
                size = parts[2]
                if size == "16":
                    template = "16"
                    price = 1536
                elif size == "32":
                    template = "32"
                    price = 6144
                elif size == "64":
                    template = "64"
                    price = 24576
                elif size == "128":
                    template = "128"
                    price = 98304
                elif size == "256":
                    template = "256"
                    price = 393216
                elif size == "512":
                    template = "512"
                    price = 1572864
                else:
                    self.client.sendServerMessage("%s is not a valid size." % size)
                    return
            else:
                self.client.sendServerMessage("Please specify a worldname and size.")
                return
            file = open('config/data/balances.dat', 'rb')
            bank = pickle.load(file)
            file.close()
            amount = price
            user = self.client.username.lower()
            if user not in bank:
                self.client.sendServerMessage("You don't have an account yet. Use /bank first.")
                return
            if not amount <= bank[user]:
                self.client.sendServerMessage("You need atleast %s to buy this world." % amount)
                return False
            else:
                file = open('config/data/balances.dat', 'wb')
                bank[user] = bank[self.client.username.lower()] - amount
                pickle.dump(bank, file)
                file.close()
                self.client.sendServerMessage("Paid %s for the world." % amount)
            world_id = parts[1].lower()
            self.client.factory.newWorld(world_id, template)
            self.client.factory.loadWorld("worlds/%s" % world_id, world_id)
            self.client.factory.worlds[world_id].all_write = False
            if len(parts) < 4:
                self.client.sendServerMessage("World '%s' made and booted." % world_id)
                self.client.changeToWorld(world_id)
                self.client.sendServerMessage(Rank(self, ["/rank", "worldowner", self.client.username, world_id], byuser, True))
            world = self.client.factory.worlds[world_id]
            world.all_write = False
