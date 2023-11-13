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
from py_helper import DebugMode, CmdLineMode, DbgMsg, Msg

# Microcontroller/Board Control
import board
import digitalio
import busio
from adafruit_motorkit import MotorKit

#
# Variables
#

parser = None
config = None

ts_tracked = "tracked"
ts_steered = "steered"
ts_fixedwheels = "fixedwheels"

motors = list()
servos = list()
steppers = list()

#
# Classes
#

class Motor:
	name = ""
	motor_obj = None
	speed = 0.0
	operations = list()

	def __init__(self, name, motor, operations=None):
		self.name = name
		self.motor_obj = motor

		if operations is not None:
			self.set_operation(operations)
		else:
			self.set_operation(["forward","reverse","turn"])

	def set_speed(self, speed=0.0):
		"""Set Motor Speed"""

		self.motor_obj.throttle = self.speed = speed

	def set_operation(self, ops):
		"""Set Valid Operations"""

		if type(ops) is list:
			for opc in ops:
				if not opc in self.operations:
					self.operations.append(opc)
		elif not ops in self.operations:
			self.operations.append(opc)

	def halt(self):
		"""Halt Motor"""

		self.set_speed(0.0)

class Motion:
	motion_strategy = "quadwheel"
	turning_strategy = "tracked"
	drive_motors = list()
	motor_groups = { }
	speed = 0

	def __init__(self):
		self.motor_groups["all"] = self.drive_motors

	def add_motor(self, motor, name=None, motor_group=None, operations=None):
		"""Add Motor"""

		if name is None:
			self.drive_motors.append(motor)
			name = motor.name
		else:
			motor = Motor(name, motor, operations=operations)
			self.drive_motors.append(motor)

		self.add_motor_to_group(motor_group, motor)

	def add_group(self, group):
		"""Add Group(s) To Motor"""

		if type(group) is list:
			for grp in group:
				self.add_group(grp)

			return
		else:
			if not group in self.motor_groups:
				self.motor_groups[group] = list()

	def add_motor_to_group(self, motor_group, motor):
		"""Add Motor to Group"""

		if type(motor_group) is list:
			for grp in motor_group:
				self.add_motor_to_group(grp, motor)

			return
		elif not motor_group in self.motor_groups:
			self.add_group(motor_group)

		self.motor_groups[motor_group].append(motor)


	def add_operation(self, operation, motor):
		"""Add Operation to Motor"""

		motor.set_operation(operation)

	def motor_group_speed(self, motor_grp = "none", speed=0.0, operation=None):
		"""Set Motor Speed By Group"""

		if motor_grp in self.motor_groups:
			for motor in self.motor_groups[motor_grp]:
				if operation is not None and operation in motor.operations:
						motor.set_speed(speed)
				else:
					motor.set_speed(speed)

	def motion(self, speed=0.0, operation=None):
		"""Set All Motors to Given Speed"""

		self.motor_group_speed("all", speed, operation=operation)
		self.speed = speed

	def motor_speed(self, motor_index, speed=0.0, operation=None):
		if motor_index < len(self.drive_motors):
			motor = self.drive_motors[motor_index]

			if operation is not None and operation in motor.operations:
				motor.set_speed(speed)
			else:
				motor.set_speed(speed)

	def left_turn(self, speed=0.8, percentage=0.5, duration=None, stop=False):
		if self.turning_strategy == ts_tracked:
			l_speed = speed * percentage
			r_speed = speed

			self.motor_group_speed("right", r_speed, operation="turn")
			self.motor_group_speed("left", l_speed, operation="turn")
		elif self.turning_strategy == ts_fixedwheels:
			self.motor_group_speed("right", speed, operation="turn")
			self.motor_group_speed("left", speed * -1, operation="turn")
		elif self.turning_strategy == ts_steered:
			# Turn Steering hardware left
			pass

		if duration is not None:
			time.sleep(duration)

			if stop:
				self.halt()
			else:
				self.motor_group_speed("left", r_speed)

	def right_turn(self, speed=0.8, percentage=0.5, duration=None, stop=False):
		if self.turning_strategy == ts_tracked:
			r_speed = speed * percentage
			l_speed = speed

			self.motor_group_speed("right", r_speed, operation="turn")
			self.motor_group_speed("left", l_speed, operation="turn")
		elif self.turning_strategy == ts_fixedwheels:
			self.motor_group_speed("right", speed * -1, operation="turn")
			self.motor_group_speed("left", speed, operation="turn")
		elif self.turning_strategy == ts_steered:
			# Turn Steering hardware right
			pass

		if duration is not None:
			time.sleep(duration)

			if stop:
				self.halt()
			else:
				self.motor_group_speed("right", l_speed)

	def forward(self, speed=0.25):
		"""Move Robot Forward"""

		if speed < 0.0:
			speed = abs(speed)

		if speed > 1.0:
			speed = 1.0

		self.motion(speed, operation="forward")

	def reverse(self, speed=-0.25):
		"""Move Robot In Reverse"""

		if speed > 0.0:
			speed = speed * -1.0

		if speed < -1.0:
			speed = -1.0

		self.motion(speed, operation="reverse")

	def halt(self):
		"""Halt Motion"""

		self.motion(0)

class adafruit_motor_control_pi_hat(Motion):
	motor_kit = None
	motor_count = 0

	def __init__(self, configin):
		super().__init__()
		self.motor_kit = MotorKit()

		self.config_me(configin)

	def config_me(self, configin):
		"""Config This Motor Control"""

		def get_ops(ops,mn):
			assigned = list()

			for op in ops.keys():
				if mn in ops[op]:
					assigned.append(op)

			return assigned

		def get_grps(grps,mn):
			assigned = list()

			for grp in grps.keys():
				if mn in grps[grp]:
					assigned.append(grp)

			return assigned

		motion = configin["motion"]
		motors = configin["adafruit_motor_control_pi_hat"]

		self.motion_strategy = motion["motion_strategy"]
		self.turning_strategy = motion["turning_strategy"]

		self.motor_count = motors.getint("count", fallback=-1)

		drives = motors["drive_motors"].split(",")
		group_names = motors["groups"].split(",")
		ops = motors["operations"].split(",")

		operations = dict()

		for op in ops:
			operations[op] = motors[op].split(",")

		groups = dict()

		for group in group_names:
			groups[group] = motors[group].split(",")

		for motor in [ "m1", "m2", "m3", "m4" ]:
			if motor in drives:
				ops = get_ops(operations,motor)
				grps = get_grps(groups,motor)

				if motor == "m1":
					motor_obj = self.motor_kit.motor1
				elif motor == "m2":
					motor_obj = self.motor_kit.motor2
				elif motor == "m3":
					motor_obj = self.motor_kit.motor3
				elif motor == "m4":
					motor_obj = self.motor_kit.motor4

				self.add_motor(motor_obj,motor,motor_group=grps,operations=ops)

class camera(ph.Taggable):
	turn_servo = None
	elevation_servo = None

	def __init__(self, configin):
		"""Init Camera Instance"""

		super().__init__()

		self.config_me(configin)

	def turn(self, distance):
		"""Turn Camera"""

		if self.turn_servo is not None:
			pass

	def elevate(self, distance):
		"""Change Elevation"""

		if self.elevation_servo is not None:
			pass

	def config_me(self, configin):
		"""Config Camera"""

		pass

class led(ph.Taggable):
	"""Mono LED"""

	name = None
	pin = None

	min = 0
	max = 10

	def __init__(self, name, config_info):
		"""Init Mono LED"""

		super().__init__()

		self.name = name

		self.config_me(config_info)

	def config_me(self, configin):
		"""Config LED"""

		# i.e. pin,min,max

		pass

class Robot(ph.Taggable):
	name = None

	platform=None
	motion_control = None
	sensors = list()
	features = list()
	camera_control = None

	def __init__(self, name="robbie", config_info=None):
		"""Init Robot"""

		super().__init__()

		self.name = name

		self.config_me(config_info)

	def config_me(self, configin):
		"""Configure Robot"""

		main = configin["main"]
		sensors = configin["sensors"]
		features = configin["features"]

		if "name" in main:
			self.name = main["name"]

		for item in main["tech_tree"].split(","):
			if item == "adafruit_motor_control_pi_hat":
				self.motion_control = adafruit_motor_control_pi_hat(configin)
			elif item == "camera":
				self.camera_control = camera(configin)

		for sensor in sensors.keys():
			pass

		for feature in features.keys():
			dev_type,info = features[feature].split(",",1)

			if dev_type == "led":
				# name is 'feature'
				pass

#
# Functions
#

def run(robot):
	"""Run: Robot Mode"""

	mc = robot.motion_control
	drives = mc.drive_motors

	m1 = drives[0]
	m2 = drives[1]
	m3 = drives[2]
	m4 = drives[3]

	mc.left_turn(percentage=0.4,duration=2.5, stop=True)

	if DebugMode():
		breakpoint()

def make_parser():
	"""Make Parser"""

	parser_obj = argparse.ArgumentParser(
		prog="MasterControl",
		description="Robot Industries Master Control Program")

	parser_obj.add_argument("-d", "--debug", action="store_true", help="Enter Debug Mode")
	parser_obj.add_argument("-t", "--test", action="store_true", help="Run test suite")

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

def test():
	"""Test Platform Stuff"""

	Msg(ph.CombiBar("Running Platform Tests"))

	# Digital PIN Test
	Msg("Running Digital IO Test : ", end="")
	pin = digitalio.DigitalInOut(board.D4)
	Msg("Digital IO OK!")

	# I2C Test
	Msg("Running I2C Test\t: ", end="")
	i2c = busio.I2C(board.SCL, board.SDA)
	Msg("I2C OK!")

	# SPI Test
	Msg("Running SPI Test\t: ", end="")
	spi = busio.SPI(board.SCLK, board.MOSI, board.MISO)
	Msg("SPI OK!")


if __name__ == "__main__":
	print("Hello, Operator!")

	parser = make_parser()

	args = parser.parse_args()

	if args.debug:
		DebugMode(True)
		CmdLineMode(True)
		DbgMsg("Entering DebugMode/CmdLineMode")

	if args.test:
		test()

	config = load_config()

	robot = Robot(config_info=config)

	run(robot)
