#
# Sparkfun Technology Module
#

import py_helper as ph
from py_helper import DebugMode, CmdLineMode, DbgMsg, Msg, Taggable

# SPI/I2C Libs
import spidev
import smbus

# Pi GPIO
import pigpio

#
# GPIO Zero Stuff
#
#import gpiozero as gpz
#from gpiozero import *

#
# Constants
#

#
# Variables
#

#
# Classes
#

class SparkfunLumenati3x3(AddressableRGBILEDModule):
	"""Sparkfun Lumenati 3x3 LED Module"""

	def __init__(self, name, description, config_section=None):
		"""Init Sparkfun Lumenati 3x3 LED Module Instance"""

		super(ProductInfo,self).__init__(
			"COM-14360",
			"Sparkfun Lumenati 3x3 LED Panel",
			"https://www.sparkfun.com/products/retired/14360?_gl=1*hzi0go*_ga*MjEzMjQ1MDQzMy4xNjk4MTg3Mjkw*_ga_T369JS7J9N*MTcwMDEwMTU1OS41LjEuMTcwMDEwMzAyMC42MC4wLjA.",
			"https://learn.sparkfun.com/tutorials/lumenati-hookup-guide/all"
			)

		self.name = name
		self.description = description

		self.leds = [[0,0,0,0]] * 9
		self.intensity_range = (0, 31)
		self.color_range = (0, 255)

		if config_section is not None:
			self.config(config_section)

	def SetIntensity(self, num, intensity):
		"""Set Intensity of LED"""

		self.leds[num][3] = intensity | 0xE0

	def WriteLEDs(self):
		"""Write Out LED Data"""

		def __spi_frame__():
			for x in range(4):
				spi.xfer2([0x00])

		__spi_frame__()

		for led in self.leds:
			r,g,b,brightness = led

			spi.xfer2([brightness])
			spi.xfer2([b])
			spi.xfer2([g])
			spi.xfer2([r])

		__spi_frame__()

	def config(self,config_section):
		"""Config Device from INI Section"""

		if "color" in config_section:
			colorspec = config_section["color"]

			rs,gs,bs,ibs = self.get_specs_sv(colorspec)

			r = int(rs)
			g = int(gs)
			b = int(bs)
			i = int(ibs)

			self.SetAll(r,g,b,i)

class SparkfunMotorDriver(MotorController):
	"""Sparkfun Dual TB6612FNG Motor Driver"""

	# Motor Config Values
	offsetA = 1
	offsetB = 1

	# Pins
	AIN1 = 2
	AIN2 = 4
	BIN1 = 7
	BIN2 = 8
	PWMA = 5
	PWMB = 6
	STBY = 9

	# 3 x GND
	# VM Pin
	# VCC
	# A01, A02, B02, B01?

	pins = {
		"AIN1": AIN1,
		"AIN2": AIN2,
		"BIN1": BIN1,
		"BIN2": BIN2,
		"PWMA": PWMA,
		"PWMB": PWMB,
		"STBY": STBY
	}

	def __init__(self, name, description, config_section=None):
		"""Initialize Instance of Motor Driver"""

		super(ProductInfo,self).__init__(
			"ROB-14451",
			"SparkFun Motor Driver - Dual TB6612FNG",
			"https://www.sparkfun.com/products/14451",
			"https://learn.sparkfun.com/tutorials/tb6612fng-hookup-guide?_gl=1*1a9ry0v*_ga*MjEzMjQ1MDQzMy4xNjk4MTg3Mjkw*_ga_T369JS7J9N*MTcwMDA5MzA0NC40LjAuMTcwMDA5MzA0NC42MC4wLjA."
			)

		self.name = name
		seld.description = description

		if config_section is not None:
			self.config(config_section)

	def config(self, section):
		"""Configure Motor Controller"""

		pass

#
# Functions
#

def sparkfun_module_tests():
	"""Test Function"""

	pass

#
# Main Loop
#

if __name__ == "__main__":
	CmdLineMode(True)

	Msg("This module is not intended to be executed by itself")
