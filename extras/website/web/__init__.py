#!/usr/bin/env python
"""web.py: makes web apps (http://webpy.org)"""



__version__ = "0.34"
__author__ = [
    "Aaron Swartz <me@aaronsw.com>",
    "Anand Chitipothu <anandology@gmail.com>"
]
__license__ = "public domain"
__contributors__ = "see http://webpy.org/changes"

from . import utils, db, net, wsgi, http, webapi, httpserver, debugerror
from . import template, form

from . import session

from .utils import *
from .db import *
from .net import *
from .wsgi import *
from .http import *
from .webapi import *
from .httpserver import *
from .debugerror import *
from .application import *
from .browser import *
from . import test
try:
    from . import webopenid as openid
except ImportError:
    pass # requires openid module

