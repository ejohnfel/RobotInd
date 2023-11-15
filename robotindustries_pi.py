#
# Robot Industries Module
#

#
# Imports
#

# Standard/System Imports

import os
import io
import re
import subprocess
import importlib

from collections import namedtuple

# Custom Imports

# My Stuff
import py_helper as ph
from py_helper import DebugMode, DbgMsg, Msg, CmdLineMode, Taggable

import gpiozero as gpz
from gpiozero import *

#
# Definitions
#

robot_elements = namedtuple("robot_elements", [ "motor_controls", "cameras", "sensors", "features" ])

#
# Constants
#

# Turn Strategy Constants
ts_tracked = "tracked"
ts_steered = "steered"
ts_fixedwheels = "fixedwheels"

# Operations
op_forward = "forward"
op_reverse = "reverse"
op_turn = "turn"
op_left_turn = "left_turn"
op_right_turn = "right_turn"
op_pan_right = "pan_right"
op_pan_left = "pan_left",
op_elevate = "elevate",
op_declinate = "declinate"

# Variables

#
# Classes
#

class Motor:
	name = ""
	motor_type = "dc"
	polarity = 1
	motor_obj = None
	speed = 0.0
	operations = list()

	def __init__(self, name, motor, operations=None, motor_type="dc", polarity=1):
		self.name = name
		self.motor_obj = motor
		self.motor_type = motor_type
		self.polarity = polarity

		if operations is not None:
			if type(operations) is list:
				self.set_operations(operations)
			else:
				self.set_operation(operations)
		else:
			default_ops = [ op_forward, op_reverse ]
			self.set_operations(default_ops)

	def set_speed(self, speed=0.0):
		"""Set Motor Speed"""

		if self.motor_obj is not None:
			self.motor_obj.throttle = self.speed = speed

	def set_operation(self, op):
		"""Set Valid Operations"""

		if not op in self.operations:
			self.operations.append(op)

	def set_operations(self, ops):
		"""Set Valid Operations"""

		for op in ops:
			self.set_operation(op)

	def halt(self):
		"""Halt Motor"""

		self.set_speed(0.0)

	def get_operations_for_motor(self, operations):
		for op_name in operations:
			if self.name in operations[op_name] and op_name not in self.operations:
				self.set_operation(op_name)

	def get_motor_operations_from_config(self, config_section):
		"""Get Motor Operations From Section"""

		config_ops = None

		if "operations" in config_section:
			config_ops = dict()

			ops = config_section["operations"].split(",")

			for op_name in ops:
				if op_name in config_section:
					if not op_name in config_ops:
						config_ops[op_name] = list()

					motor_names = config_section[op_name].split(",")

					for motor_name in motor_names:
						config_ops[op_name].append(motor_name)

		return config_ops

	def get_dc_motor_definition(self, parameters):
		"""Get DC Motor Definition From Data"""

		self.motor_type = parameters["type"]
		self.polarity = int(parameters["polarity"])

	def get_motor_definition(self, motor_definition):
		"""Get Motor Definiton and Call Correct Def Conversion"""

		fields = motor_definition.split(",")

		parameters = dict()

		for field in fields:
			name,value = field.split(":")

			parameters[name] = value

		if parameters["type"] == "dc":
			self.get_dc_motor_definition(parameters)

	def config(self, config_section):
		"""Configure motor using INI Section"""

		if self.name in config_section:
			motor_definition = config_section[self.name]

			self.get_motor_definition(motor_definition)

		if "operations" in  config_section:
			ops = self.get_motor_operations_from_config(config_section)
			self.get_operations_for_motor(ops)

class MotorController(Taggable):
	"""Motor Controller"""

	name = "motorcontroller"
	description = None

	turning_strategy = ts_fixedwheels

	motors = list()

	motor_groups = dict()

	controller = None

	def __init__(self, name, description=None, controller=None):
		"""Initialize Motor Controller Instance"""

		self.name = name
		self.description = description
		self.controller = controller
		self.motor_groups["all"] = self.motors

	def add_group(self, group):
		"""Add Group(s) To MotorController"""

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
				elif operation is None:
					motor.set_speed(speed)

	def motion(self, speed=0.0, operation=None):
		"""Set All Motors to Given Speed"""

		self.motor_group_speed("all", speed, operation=operation)

	def motor_speed(self, motor_index, speed=0.0, operation=None):
		if motor_index < len(self.drive_motors):
			motor = self.motors[motor_index]

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

	def get_motor_groups(self, groups):
		"""Get Group Memberships for Motors"""

		"""Support function to extract group members from INI"""

		for motor in self.motors:
			motor_name = motor.name

			for group in groups:
				if motor_name in groups[group]:
					self.add_group(group)

					self.motor_groups[group].append(motor)

	def config(self, config_section):
		"""Config Motor Controller"""

		self.turning_strategy = config_section.get("turing_strategy", fallback=ts_fixedwheels)

		# Get Groups, set group memberships
		# Get operations, set motor operations

		groups = None
		memberships = dict()

		if "groups" in config_section:
			groups = config_section["groups"].split(",")

			for group in groups:
				members = config_section.get(group, fallback="").split(",")

				memberships[group] = members

			self.get_motor_groups(memberships)
		else:
			DbgMsg(f"No groups label in config section for {self.name}")

		for motor in self.motors:
			motor.config(config_section)

class Camera(Taggable):
	"""Camera Class"""

	def __init__(self):
		"""Initialize Camera Instance"""

		pass

class Sensor(Taggable):
	"""Sensor Class"""

	def __init__(self):
		"""Initialize Sensor Instance"""

		pass

class Feature(Taggable):
	"""Feature Class"""

	def __init__(self):
		"""Initialize Feature Instance"""

		pass

class Robot(Taggable):
	"""Robot Class"""

	name = None
	description = None
	vendors = dict()

	motor_controls = dict()
	sensors = list()
	features = list()
	cameras = list()

	elements = None

	runloop = None

	config_elements = None

	def __init__(self, name="robbie", config_info=None, run=None):
		"""Init Robot"""

		super().__init__()

		self.name = name
		self.description = "Just a robot in a human world"
		self.runloop = run

		self.config_elements = config_info

		if not self.config_elements is None:
			self.elements = self.config(self.config_elements)

	def add(self, item):
		if isinstance(item,MotorController):
			self.motor_controls[item.name] = item
		elif isinstance(Camera):
			pass
		elif isinstance(Sensor):
			pass
		elif isinstance(Feature):
			pass

	def run(self,args=None,kwargs=None):
		"""Execute Run Loop"""

		if self.runloop is not None:
			self.runloop()

	def get_element_section(self, section_label):
		"""Get Element Config Section From INI"""

		section = None

		if self.config_elements is not None:
			if section_label in self.config_elements:
				section = self.config_elements[section_label]
			else:
				DbgMsg(f"There is no section label {section_label} in INI file")
		else:
			DbgMsg(f"No robot INI file loaded")

		return section

	def config(self, config_info):
		"""Configure Robot"""

		main = config_info["main"]

		self.name = main.get("name", fallback="robbie")
		self.description = main.get("description", fallback="Justa robot in a human world")

		vendors = main.get("vendors", fallback="").split(",")
		for vendor in vendors:
			self.vendors[vendor] = None

			# check namspace if not there, import
			# if there OR imported, check for "build_out"
			# and add to vendors[vendor]
			#importlib.import_module(vendor)

		motor_controls = dict()
		cameras = dict()
		sensors = dict()
		features = dict()

		if "motor_controls" in config_info:
			mcs = config_info["motor_controls"]

			for mc in mcs:
				motor_controls[mc] = mcs[mc]

		if "cameras" in config_info:
			cams = config_info["cameras"]

			for cam in cams:
				cameras[cam] = cams[cam]

		if "sensors" in config_info:
			sens = config_info["sensors"]

			for sensor in sens:
				sensors[sensor] = sens[sensor]

		if "features" in config_info:
			feats = config_info["features"]

			for feat in feats:
				features[feat] = feats[feat]

		elements = robot_elements(motor_controls, cameras, sensors, features)

		return elements