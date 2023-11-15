#!/usr/bin/env python

#
# Imports
#

# Python Stuff
import io
import os
import re
import argparse
import configparser
import time
import random
import py_helper as ph

# Froms

from datetime import datetime

# Py Helper Stoof
import py_helper as ph
from py_helper import DebugMode, CmdLineMode, DbgMsg, Msg

import gpiozero as pgz
from gpiozero import *

# Robot Industries
from robotindustries_pi import *
import adafruit_pi as ap
from adafruit_pi import adafruit_motor_control

#
# Variables
#

config_file = "arwen.ini"

parser = None
config = None

#
# Functions
#

def run(args=None,kwargs=None):
	"""Run: Robot Mode"""

	if DebugMode():
		breakpoint()

def make_parser():
	"""Make Parser"""

	parser_obj = argparse.ArgumentParser(
		prog="MasterControl",
		description="Robot Industries Master Control Program")

	parser_obj.add_argument("-d", "--debug", action="store_true", help="Enter Debug Mode")
	parser_obj.add_argument("-t", "--test", action="store_true", help="Run test suite")
	parser_obj.add_argument("-c", "--config", help="Config file for robot")

	return parser_obj

def load_config(config_file=None):
	"""Load Config File"""

	config_obj = None

	if config_file is None:
		config_file = "config.ini"

	if os.path.exists(config_file):
		config_obj = configparser.ConfigParser()

		config_obj.read(config_file)

	return config_obj

def test(config, robot):
	"""Test Platform Stuff"""

	Msg(ph.CombiBar("Running Platform Tests"))

	# Digital PIN Test
	Msg("Running Digital IO Test : ", end="")
	#pin = digitalio.DigitalInOut(board.D4)
	Msg("Digital IO OK!")

	# I2C Test
	Msg("Running I2C Test\t: ", end="")
	#i2c = busio.I2C(board.SCL, board.SDA)
	Msg("I2C OK!")

	# SPI Test
	Msg("Running SPI Test\t: ", end="")
	#spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
	Msg("SPI OK!")


if __name__ == "__main__":
	print("Hello, Operator!")

	parser = make_parser()

	args = parser.parse_args()

	if args.debug:
		DebugMode(True)
		CmdLineMode(True)
		DbgMsg("Entering DebugMode/CmdLineMode")

	if args.config is not None:
		config_file = args.config

	config = load_config(config_file)

	robot = Robot(config_info=config,run=run)

	built_elements = ap.adafruit_build_out(robot)

	if args.test:
		test(config, robot)
	else:
		robot.run()


