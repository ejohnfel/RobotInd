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

from collections import namedtuple

# Custom Imports

# My Stuff
import py_helper as ph
from py_helper import DebugMode, DbgMsg, Msg, CmdLineMode, Taggable

# SPI/I2C Libs
import spidev
import smbus

# Might uses these as "PIN TYPE"
pt_pi = 0
pt_broadcom = 1
pt_arduino = 2
pt_other = 3

pin_mappings = { }

import gpiozero as gpz

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

# SPI Control
__spi__ = None

#
# Classes
#

class ProductInfo(Taggable):
	"""Product Info Class"""

	manufacturer = ""
	product_name = ""
	part_number = ""
	product_description = ""
	product_url = ""
	documentation = ""
	notes = ""

	def __init__(self, product_name="", partnumber="", description="", url="", documentation="", manufacturer="", config_section=None):
		"""Init Product Info Instance"""

		super().__init__()

		self.manufacturer = manufacturer
		self.product_name = product_name
		self.part_number = partnumber
		self.product_description = description
		self.product_url = url
		self.documentation = documentation

		if config_section is not None:
			self.config(config_section)

	def get_specs_sv(self, specs, seperator=","):
		"""Get Device specs from one line INI as a list of Separated values"""

		spec_list = specs.split(seperator)

		return spec_list

	def get_specs_dict(self, specs):
		"""Get device specs from one line INI as a Dictionary"""

		spec_dict = dict()

		if type(specs) is str:
			specs = self.get_specs_sv(specs)
		elif type(specs) is list:
			pass

		for spec in specs:
			field, value = self.get_specs_sv(spec,":")

			spec_dict[field] = value

		return spec_dict

	def pin_map(pin, pin_type=pt_pi):
		"""Map Given Pin to pigpio PIN"""

		return pin

	def config(self, config_section):
		"""Extract Product Info From INI"""

		if "manufacturer" in config_section:
			self.manufacturer = config_section.get("manufacturer", fallback="No manufacturer provided")
		if "product_name" in config_section:
			self.product_name = config_section.get("product_name", fallback="No product name provided")
		if "product_number" in config_section:
			self.product_number = config_section.get("product_number", fallback="No product number provided")
		if "product_description" in config_section:
			self.product_description = config_section.get("product_description", fallback="No description provided")
		if "product_url" in config_section:
			self.product_url = config_section.get("product_url", fallback="No URL Provided")
		if "documentation" in config_section:
			self.documentation = config_section.get("documentation", fallback="No documentation provided")
		if "notes" in config_section:
			self.notes = config_section.get("notes", fallback="No notes")

class DeviceInfo(ProductInfo):
	"""Device Information"""

	name = None
	description = None

	def __init__(self, name="device", description="no description", config_section=None):
		"""Init DeviceInfo Instance"""

		super("ProductInfo",self).__init__(config_section)

		if name is not None:
			self.name = name

		if description is not None:
			self.description = description

		self.config(config_section)

	def config(self, config_section):
		"""Config Instance"""

		if "name" in config_section:
			self.name = config_section["name"]

		if "description" in config_section:
			self.name = config_section["description"]

class DigitalGPIODevice(DeviceInfo):
	"""Simple DigitalGPIO Device"""

	pin = None

	def __init__(self, pin=None, name=None, description=None, config_section=None):
		"""Initialize Instance of Digital GPIO Device"""

		if pin is not None:
			self.pin = pin

		super(DeviceInfo,self).__init__(name, description, config_section=config_section)

		if config_section is not None:
			self.config(config_section)

	def read(self):
		"""Read from PIN"""

		value = None

		# TODO : convert to gpiozero

		#if self.pig_obj is not None and self.pin is not None:
		#	self.pig_obj.set_mode(self.pin, pigpio.INPUT)
		#	value = self.pig_obj.read(self.pin)

		return value

	def write(self, value):
		"""Write to PIN"""

		# TODO : Convert to gpiozero

		#if self.pig_obj is not None and self.pin is not None:
		#	self.pig_obj.set_mode(self.pin, pigpio.OUTPUT)
		#	self.pig_obj.write(self.pin, value)

		pass

	def config(self, config_section):
		"""Config Device from INI Section"""

		if "pin" in config_section:
			self.pin = config_section.getint("pin", fallback=None)

class I2CDevice():
	"""I2C Bus Communications"""

	address = None

	def __init__(self, address):
		"""Init I2C Comm Instance"""

		self.address = address

class SPIDevice():
	"""SPI Bus Device"""

	__spi__ = None
	bus = 0
	device = 0
	bus_speed = 500000

	def __init__(self, bus=0, device=0, bus_speed=500000, config_section=None):
		"""Init SPI Comm Instance"""

		self.bus = bus
		self.device = device
		self.__spi__ = spidev.SpiDev()
		self.set_bus_speed(bus_speed)

		if config_section is not None:
			self.config(config_section)

	def set_bus_speed(self, speed):
		"""Set Bus Speed"""

		self.bus_speed = speed

		self.__spi__.max_speed_hertz = self.bus_speed

	def config(self, config_section):
		"""Config Instance"""

		if "spi_bus" in config_section:
			self.bus = config_section.getint("spi_bus", fallback=0)

		if "spi_device" in config_section:
			self.device = config_section.getint("spi_device", fallback=0)

		if "spi_bus_speed" in config_section:
			self.set_bus_speed(config_section.get("spi_bus_speed", fallback=500000))

	def open(self):
		"""Open SPI Bus"""

		self.__spi__.open(self.bus, self.device)

	def readbytes(self,length):
		"""Read Bytes Wrapper"""

		return self.__spi__.readbytes(length)

	def writebytes(self, values):
		"""Write Bytes SPI Wrapper"""

		self.__spi__.writebytes(values)

	def writebytes2(self, values):
		"""Write Bytes SPI Wrapper"""

		self.__spi__.writebytes2(values)

	def xfer(self, values, speed=None, delay=None, bits=None):
		"""XFer Data Wrapper"""

		rcvd = self.__spi__.xfer(values, speed, delay, bits)

		return rcvd

	def xfer2(self, values, speed=None, delay=None, bits=None):
		"""XFer 2 Wrapper"""

		rcvd = self.__spi__.xfer2(values, speed, delay, bits)

		return rcvd

	def xfer3(self, values, speed=None, delay=None, bits=None):
		"""XFer 3 Wrapper"""

		rcvd = self.__spi__.xfer3(values, speed, delay, bits)

		return rcvd

	def close(self):
		"""Close SPI Bus"""

		self.__spi__.close()

	@property
	def threewire(self):
		"""Threewire wrapper"""

		return self.__spi__.threewire

	@threewire.setter
	def threewire(self, value):
		"""Threewire wrapper Setter"""

		self.__spi__.threewire = value

	@property
	def mode(self):
		"""Mode Wrapper"""

		return self.__spi__.mode

	@mode.setter
	def mode(self, value):
		"""Mode Wrapper Setter"""

		self.__spi__.mode = value

	@property
	def max_speed_hz(self):
		"""Max Speed Hz Wrapper"""

		return self.__spi__.max_speed_hz

	@max_speed_hz.setter
	def max_speed_hz(self, value):
		"""Max Speed Hz Wrapper Setter"""

		self.__spi__.max_speed_hz = value

	@property
	def lsbfirst(self):
		"""LSB First Wrapper"""

		return self.__spi__.lsbfirst

	@lsbfirst.setter
	def lsbfirst(self, value):
		"""LSB First Wrapper Setter"""

		self.__spi__.lsbfirst = value

	@property
	def loop(self):
		"""Loop Wrapper"""

		return self.__spi__.loop

	@loop.setter
	def loop(self, value):
		"""Loop Wrapper Setter"""

		self.__spi__.loop = value

	@property
	def cshigh(self):
		"""CS High Wrapper"""

		return self.__spi__.cshigh

	@cshigh.setter
	def cshigh(self, value):
		"""CSHigh Wrapper Setter"""

		self.__spi__.cshigh = value

	@property
	def bits_per_word(self):
		"""Bits Per Word Wrapper"""

		return self.__spi__.bits_per_word

	@bits_per_word.setter
	def bits_per_word(self, value):
		"""Bits Per Word Wrapper Setter"""

		self.__spi__.bits_per_word = value

class Motor(DeviceInfo):
	"""Motor Device"""

	motor_type = "dc"
	polarity = 1
	trim = 0.0
	motor_obj = None
	speed = 0.0
	operations = list()

	def __init__(self, name=None, description=None, motor=None, operations=None, motor_type="dc", polarity=1, trim=0.0, config_section=None):
		if name is not None:
			self.name = name
		if description is not None:
			self.description = description

		self.motor_obj = motor
		self.motor_type = motor_type
		self.polarity = polarity
		self.trim = trim

		super(DeviceInfo,self).__init__(config_section=config_section)

		if operations is not None:
			if type(operations) is list:
				self.set_operations(operations)
			else:
				self.set_operation(operations)
		else:
			default_ops = [ op_forward, op_reverse ]
			self.set_operations(default_ops)

		if config_section is not None:
			self.config(config_section)

	def trimmed(self, speed):
		"""Trim Speed"""

		if speed != 0:
			speed -= self.trim

		return speed

	def set_speed(self, speed=0.0):
		"""Set Motor Speed"""

		if self.motor_obj is not None:
			self.motor_obj.throttle = self.speed = (self.trimmed(speed) * self.polarity)

	def set_trim(self, value):
		"""Set Trim Value"""

		self.trim = value

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

			ops = self.get_specs_sv(config_section["operations"])

			for op_name in ops:
				if op_name in config_section:
					if not op_name in config_ops:
						config_ops[op_name] = list()

					motor_names = self.get_specs_sv(config_section[op_name])

					for motor_name in motor_names:
						config_ops[op_name].append(motor_name)

		return config_ops

	def get_dc_motor_definition(self, specs):
		"""Get DC Motor Definition From Data"""

		self.motor_type = specs["type"]
		self.polarity = int(specs["polarity"])
		self.trim = float(specs["trim"])

	def get_motor_definition(self, motor_definition):
		"""Get Motor Definiton and Call Correct Def Conversion"""

		specs = self.get_specs_dict(motor_definition)

		if "description" in specs:
			self.description = specs["description"]

		if specs["type"] == "dc":
			self.get_dc_motor_definition(specs)
		elif specs["type"] == "ac":
			pass
		elif specs["type"] == "stepper":
			pass
		elif specs["type"] == "servo":
			pass

	def config(self, config_section):
		"""Configure motor using INI Section"""

		if self.name in config_section:
			motor_definition = config_section[self.name]

			self.get_motor_definition(motor_definition)

		if "operations" in  config_section:
			ops = self.get_motor_operations_from_config(config_section)
			self.get_operations_for_motor(ops)

class MotorController(DeviceInfo):
	"""Motor Controller"""

	turn_differential = 0.2
	turning_strategy = ts_fixedwheels

	motors = list()

	motor_groups = dict()

	controller = None

	def __init__(self, name=None, description=None, controller=None, turn_diff=0.2, config_section=None):
		"""Initialize Motor Controller Instance"""

		if name is not None:
			self.name = name
		if description is not None:
			self.description = description

		self.controller = controller
		self.motor_groups["all"] = self.motors
		self.turn_differential = turn_diff

		if config_section is not None:
			self.config(config_section)

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

	def left_turn(self, speed=1.0, duration=None, stop=False):

		diff_speed = speed - self.turn_differential

		if self.turning_strategy == ts_tracked:
			self.motor_group_speed("right", speed, operation="left_turn")
			self.motor_group_speed("left", diff_speed, operation="left_turn")
		elif self.turning_strategy == ts_fixedwheels:
			self.motor_group_speed("right", speed, operation="left_turn")
			self.motor_group_speed("left", (diff_speed * -1.0), operation="left_turn")
		elif self.turning_strategy == ts_steered:
			# Turn Steering hardware left
			pass

		if duration is not None:
			time.sleep(duration)

			if stop:
				self.halt()
			else:
				self.motor_group_speed("left", speed)

	def right_turn(self, speed=1.0, duration=None, stop=False):

		diff_speed = speed - self.turn_differential

		if self.turning_strategy == ts_tracked:
			self.motor_group_speed("right", diff_speed, operation="right_turn")
			self.motor_group_speed("left", speed, operation="right_turn")
		elif self.turning_strategy == ts_fixedwheels:
			self.motor_group_speed("right", (diff_speed * -1), operation="right_turn")
			self.motor_group_speed("left", speed, operation="right_turn")
		elif self.turning_strategy == ts_steered:
			# Turn Steering hardware right
			pass

		if duration is not None:
			time.sleep(duration)

			if stop:
				self.halt()
			else:
				self.motor_group_speed("right", speed)

	def forward(self, speed=0.5):
		"""Move Robot Forward"""

		if speed < 0.0:
			speed = abs(speed)

		if speed > 1.0:
			speed = 1.0

		self.motion(speed, operation="forward")

	def reverse(self, speed=-0.5):
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

		self.turning_strategy = config_section.get("turning_strategy", fallback=ts_fixedwheels)

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

class LED(DigitalGPIODevice):
	"""Simple LED"""

	def __init__(self, pig_obj, pin=None, name=None, description=None, config_section=None):
		"""Initialize LED Instance"""

		super().__init__(pin, name=name, description=description, config_section=config_section)

	def on(self):
		self.write(1)

	def off(self):
		self.write(0)

	def config(self, config_section):
		"""Config Instance"""

		pass

class Camera(ProductInfo):
	"""Camera Class"""

	def __init__(self):
		"""Initialize Camera Instance"""

		pass

class Sensor(ProductInfo):
	"""Sensor Class"""

	def __init__(self):
		"""Initialize Sensor Instance"""

		pass

class Feature(ProductInfo):
	"""Feature Class"""

	def __init__(self):
		"""Initialize Feature Instance"""

		pass

class Robot(ProductInfo):
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

	def run(self, *args, **kwargs):
		"""Execute Run Loop"""

		if self.runloop is not None:
			self.runloop(self, args, kwargs)

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
