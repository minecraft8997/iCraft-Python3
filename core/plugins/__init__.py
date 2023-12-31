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

import logging, sys
import importlib

protocol_plugins = []
server_plugins = []

class PluginMetaclass(type):
    
    """
    A metaclass which registers any subclasses of Plugin.
    """
    
    def __new__(cls, name, bases, dct):
        # Supercall
        new_cls = type.__new__(cls, name, bases, dct)
        # Register!
        if bases != (object,):
            if ProtocolPlugin in bases:
                logging.log(logging.DEBUG, "Loaded protocol plugin: %s" % name)
                protocol_plugins.append(new_cls)
            elif ServerPlugin in bases:
                logging.log(logging.DEBUG, "Loaded server plugin: %s" % name)
                server_plugins.append(new_cls)
            else:
                logging.log(logging.WARN, "Plugin '%s' is not a server or a protocol plugin." % name)
        return new_cls


class ServerPlugin(object, metaclass=PluginMetaclass):
    """
    Parent object all plugins inherit from.
    """


class ProtocolPlugin(object, metaclass=PluginMetaclass):
    """
    Parent object all plugins inherit from.
    """
    
    def __init__(self, client):
        # Store the client
        self.client = client
        # Register our commands
        if hasattr(self, "commands"):
            for name, fname in list(self.commands.items()):
                self.client.registerCommand(name, getattr(self, fname))
        # Register our hooks
        if hasattr(self, "hooks"):
            for name, fname in list(self.hooks.items()):
                self.client.registerHook(name, getattr(self, fname))
        # Call clean setup method
        self.gotClient()
    
    def unregister(self):
        # Unregister our commands
        if hasattr(self, "commands"):
            for name, fname in list(self.commands.items()):
                self.client.unregisterCommand(name, getattr(self, fname))
        # Unregister our hooks
        if hasattr(self, "hooks"):
            for name, fname in list(self.hooks.items()):
                self.client.unregisterHook(name, getattr(self, fname))
        del self.client
    
    def gotClient(self):
        pass


def load_plugins(plugins):
    "Given a list of plugin names, imports them so they register."
    #fucking ikjames the retard decided to force Interact on everything. Fuck you idiot. Nobody likes you.
    for module_name in plugins:
        try:
            __import__("core.plugins.%s" % module_name)
        except ImportError:
            logging.log(logging.ERROR, "Cannot load plugin %s." % module_name)


def unload_plugin(plugin_name):
    "Given a plugin name, reloads and re-imports its code."
    # Unload all its classes from our lists
    for plugin in plugins_by_module_name(plugin_name):
        if plugin in protocol_plugins:
            protocol_plugins.remove(plugin)
        if plugin in server_plugins:
            server_plugins.remove(plugin)


def load_plugin(plugin_name):
    # Reload the module, in case it was imported before
    importlib.reload(__import__("core.plugins.%s" % plugin_name, {}, {}, ["*"]))
    load_plugins([plugin_name])


def plugins_by_module_name(module_name):
    "Given a module name, returns the plugin classes in it."
    try:
        module = __import__("core.plugins.%s" % module_name, {}, {}, ["*"])
    except ImportError:
        raise ValueError("Cannot load plugin %s." % module_name)
    else:
        for name, val in list(module.__dict__.items()):
            if isinstance(val, type):
                if issubclass(val, ProtocolPlugin) and val is not ProtocolPlugin:
                    yield val
                elif issubclass(val, ServerPlugin) and val is not ServerPlugin:
                    yield val
