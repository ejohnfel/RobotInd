#!/bin/env python

#
# Robot Industries - Flask Based Robot Control Interface
#

# Imports

import os
import sys
import io
import re
import argparse
import configparser

# Custom Modules
import py_helper as ph
from py_helper import DebugMode, DbgMsg, Msg, CmdLineMode

# Flask

import flask
from flask import Flask
from flask import request

#
# Top Level Flask Instance
#
app = Flask(__name__)


#
# Constants
#

#
# Variables
#

#
# Classes
#

#
# Lambdas
#

#
# Functions
#

#
# Flask Code
#

@app.route("/")
def index():
	"""Main Index of Gui Control"""

	return "<h1>Hello, World!</h1>"

@app.route("/credits")
def credits():
	"""Credits Page"""

	return "<h1>Credits : I don't give credit, because no one else does. However, Juju, my feline overlord says she is the only one creditable for this. I fear she will take control of my robots and then I am really in trouble... send help...</h1>"

#
# Internal Functions
#

#
# Main Loop
#

if __name__ == "__main__":
	print("This module was not meant to be run on it's own")
