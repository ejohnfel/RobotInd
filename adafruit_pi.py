#
# Robot Industries Adafruit Module/Hardware/Platform Module
#

import py_helper as ph
from py_helper import DebugMode, CmdLineMode, DbgMsg, Msg, Taggable

# SPI/I2C Libs
import spidev
import smbus

# PI GPIO
import pigpio

# GPIO Zero Stuff
#import gpiozero as gpz
#from gpiozero import *

# Microcontroller/Board Control/Circuit Playground Stuff
import board
import digitalio
import busio
from adafruit_motorkit import MotorKit

from robotindustries_pi import *

#
# Classes
#

class adafruit_motor_control(MotorController):
	"""Adafruit Motor Class"""

	def __init__(self, name, description=None):
		super().__init__(name, description, MotorKit())

		m1 = Motor("m1", self.controller.motor1, None, "dc", 1)
		m2 = Motor("m2", self.controller.motor1, None, "dc", 1)
		m3 = Motor("m3", self.controller.motor1, None, "dc", 1)
		m4 = Motor("m4", self.controller.motor1, None, "dc", 1)

		self.motors.extend([ m1, m2, m3, m4 ])

	def config(self, element_section=None):
		"""Config Motor Controller Instance"""

		super().config(element_section)


#
# Functions
#

def adafruit_build_out(robot):
	"""Run through elements, pick out Adafruit Hardware and build them out"""

	built_elements = list()

	my_devices = list(["adafruit_motor_control"])

	elements = [
		robot.elements.motor_controls,
		robot.elements.cameras,
		robot.elements.sensors,
		robot.elements.features ]

	for element in elements:
		for device in element:
			section_label = element[device]

			section = robot.get_element_section(section_label)

			if section is not None:
				if "hardware" in section:
					description = section.get("description", fallback="No description")
					device_type = section["hardware"]

					if device_type in my_devices:
						if device_type == "adafruit_motor_control":
							mc = adafruit_motor_control(section_label, description)
							mc.config(section)

							built_elements.append(mc)

							robot.add(mc)
				else:
					DbgMsg("'hardware' not in section")
			else:
				DbgMsg(f"Attempt to get element section, {section_label}, from robot INI failed")

	return built_elements

def adafruit_module_tests():
	"""Test Function"""

	pass

#
# Main Loop
#


if __name__ == "__main__":
	CmdLineMode(True)

	Msg("This module is not intended to be executed by itself")
