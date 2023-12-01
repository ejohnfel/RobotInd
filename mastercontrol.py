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

from signal import pause
from datetime import datetime

# Py Helper Stoof
import py_helper as ph
from py_helper import DebugMode, CmdLineMode, DbgMsg, Msg

# Electronics Stuff

import gpiozero as pgz
from gpiozero import *

from bluedot import BlueDot

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

# Control Variables

running = True
robot = None

#
# Functions
#

def exit_press(pos):
	"""Blue Dot Exit Press Handler"""
	global running

	DbgMsg("Exiting...")

	running = False

def led_press(pos):
	"""LED Toggle"""

	pass

def forward_press(pos):
	"""Forward Press"""

	DbgMsg("Moving Forward...")
	mc = robot.motor_controls["primary_drive"]

	mc.forward(1.0)

def forward_release(pos):
	"""Forward Release"""

	DbgMsg("Stopping Forward")
	mc = robot.motor_controls["primary_drive"]

	mc.halt()

def reverse_press(pos):
	"""Reverse Press"""

	DbgMsg("Moving In Reverse...")
	mc = robot.motor_controls["primary_drive"]

	mc.reverse(1.0)

def reverse_release(pos):
	"""Reverse Release"""

	DbgMsg("Stopping Reverse")
	mc = robot.motor_controls["primary_drive"]

	mc.halt()

def left_press(pos):
	"""Left Press"""

	DbgMsg("Turning Left...")
	mc = robot.motor_controls["primary_drive"]

	mc.left_turn(1.0)

def left_release(pos):
	"""Left Release"""

	DbgMsg("Stopping Left...")
	mc = robot.motor_controls["primary_drive"]

	mc.halt()

def right_press(pos):
	"""Right Press"""

	DbgMsg("Turning Right...")
	mc = robot.motor_controls["primary_drive"]

	mc.right_turn(1.0)

def right_release(pos):
	"""Right Release"""

	DbgMsg("Stopping Right...")
	mc = robot.motor_controls["primary_drive"]

	mc.halt()

def halt_press(pos):
	"""Halt Press"""

	DbgMsg("Halting...")
	mc = robot.motor_controls["primary_drive"]

	mc.halt()

def servo_left(pos):
	"""Servo Left"""

	DbgMsg("Servo Left...")

def servo_right(pos):
	"""Servo Right"""

	DbgMsg("Servo Right...")

def servo_up(pos):
	"""Servo Up"""

	DbgMsg("Servo Up ...")

def servo_down(pos):
	"""Servo Down"""

	DbgMsg("Servo Down...")

def run(robot, *args, **kwargs):
	"""Run: Robot Mode"""
	global running

	#   For
	# L  H  R X		(motors)
	#   Rev   LED
	# L  U  D R		(servos)
	bd = BlueDot(cols=4,rows=4)
	bd[0,0].visible = bd[2,0].visible = bd[3,0].visible = False
	bd[1,1].color = "red"
	bd[1,1].square = True
	bd[3,1].color = "yellow"
	bd[0,2].visible = bd[2,2].visible = bd[3,2].visible = False

	# Forward
	bd[1,0].when_pressed = forward_press
	bd[1,0].when_released = forward_release
	bd[1,0].square = True

	# Halt
	bd[1,1].when_pressed = halt_press
	bd[1,1].square = True

	# Reverse
	bd[1,2].when_pressed = reverse_press
	bd[1,2].when_released = reverse_release
	bd[1,2].square = True

	# left
	bd[0,1].when_pressed = left_press
	bd[0,1].when_released = left_release
	bd[0,1].square = True

	# Right
	bd[2,1].when_pressed = right_press
	bd[2,1].when_released = right_release
	bd[2,1].square = True

	# Exit
	bd[3,1].when_pressed = exit_press
	bd[3,2].when_pressed = led_press

	# Servo
	bd[0,3].when_pressed = servo_left
	bd[1,3].when_pressed = servo_up
	bd[2,3].when_pressed = servo_down
	bd[3,3].when_pressed = servo_right

	while running:
		pause

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

		if "main" in config_obj:
			if "debugmode" in config_obj["main"]:
				DebugMode(config_obj["main"].getboolean("debugmode",fallback=False))

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


