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

import py_helper as ph
from py_helper import DebugMode, CmdLineMode, DbgMsg, Msg

# Custom Modules
import py_helper as ph
from py_helper import DebugMode, DbgMsg, Msg, CmdLineMode

# Flask

import flask
from flask import Flask
from flask import request, abort, redirect

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

# Config Section
config = None
LoginEnabled = False
CurrentUser = None

# Login Enabled

#
# Classes
#

#
# Lambdas
#

#
# Functions
#

def ConfigWebGui(config_section=None):
	"""Config Control With Config Section"""

	config = config_section

	CurrentUser = None
	LoginEnabled = config.getboolean("login", fallback=False)

def Banner(msg):
	"""Shortcut Msg"""

	return f"<h1>{msg}</h1>"

#
# Flask Code
#

@app.route("/")
def router():
	"""The Initial Router"""

	# TODO: Got to fix this global/context variable issue
	LoginEnabled = True

	if LoginEnabled:
		return redirect("/login")

	return redirect("/main")

@app.route("/login")
def login():
	"""Login Route"""

	return Banner("Login Route")

@app.route("/main")
def main():
	"""Main Control Window"""

	return Banner("Main Route")

@app.route("/credits")
def credits():
	"""Credits Page"""

	return "<h1>Credits : I don't give credit, because no one else does. However, Juju, my feline overlord says she is the only one creditable for this. I fear she will take control of my robots and then I am really in trouble... send help...</h1>"

#
# Internal Functions
#

def create_parser():
	"""Create Parser"""

	parser = argparse.ArgumentParser(prog="ri_flask", description="Robot Industries Flask Argument Parser")

	parser.add_argument("--host", help="Set host interface to operate on")


	return parser

def load_config(filename):
	"""Load Config File"""

	config_obj = configparser.ConfigParser()

	if os.path.exists(filename):
		config_obj.read(filename)
	else:
		DebugMode(True)
		CmdLineMode(True)

		DbgMsg(f"INI, {filename}, File does not exist")


	return config_obj

def test():
	"""Test Function"""

	pass

#
# Main Loop
#

if __name__ == "__main__":
	print("This module was not meant to be run on it's own")

	CmdLineMode(True)

	cfg_obj = load_config("arwen.ini")

	main_section = cfg_obj["main"]

	if main_section.getboolean("debugmode", fallback=False):
		DebugMode(True)
		CmdLineMode(True)
		DbgMsg("Entering Debug Mode")

	if "webgui" in cfg_obj:
		ConfigWebGui(cfg_obj["webgui"])

		app.run(host="0.0.0.0")
	else:
		print("No webgui section present in INI file")
