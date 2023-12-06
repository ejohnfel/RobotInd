#
# Sparkfun Technology Module
#

import py_helper as ph
from py_helper import DebugMode, CmdLineMode, DbgMsg, Msg, Taggable

# SPI/I2C Libs
import spidev
import smbus

#
# GPIO Zero Stuff
#
import gpiozero as gpz

#
# Robot Industries Module
#
from robotindustries_pi import *

#
# Constants
#

#
# Variables
#

#
# Classes
#

class SparkfunLumenati(DeviceInfo, SPIDevice):
	"""Sparkfun Lumenati Base Class"""

	pixels = None

	_max_brightness = 31
	_min_brightness = 0
	_max_color = 255
	_min_color = 0

	white = None
	black = None
	off = None
	on = None
	red = None
	green = None
	blue = None
	yellow = None
	purple = None

	def __init__(self, pixels, bus=None, device=None, bus_speed=500000, config_section=None):
		"""Initialize Instance"""

		if bus is None:
			bus = 0

		if device is None:
			device = 0

		super(SPIDevice,self).__init__(bus, device, bus_speed, config_section=config_section)

		self.pixels = [[0,0,0,0]] * pixels

		self.white = self.on = ( 255, 255, 255)
		self.black = self.off = ( 0, 0, 0 )
		self.red = ( 255, 0, 0 )
		self.green = ( 0, 255, 0 )
		self.blue = ( 0, 0, 255 )
		self.yellow = ( 255, 255, 0 )
		self.purple = ( 128, 0, 255 )

		if config_section is not None:
			self.config(config_section)

	def config(self, section_config):
		"""Configure Instance"""

		if "pixels" in config_section:
			self.pixels = [[0,0,0,0]] * config_section.getint("pixels", fallback=1)

	def _start_frame(self):
		"""Start Frame of APA102C Pixels"""

		data = [ 0, 0, 0, 0 ]

		return data

	def _end_frame():
		"""End Frame of APA102C Pixels"""

		data = [ 0xff, 0xff, 0xff, 0xff ]

		return data

	def _brightness_check(self, brightness):
		"""Enforce Brightness Settings"""

		brightness = 16 if brightness > self._max_brightness or brightness < self._min_brightness else brightness

		return brightness

	def _color_check(self, color):
		"""Enforce Color Value Min/Max"""

		color = 128 if color > self._max_color or color < self.min_color else color

		return color

	def write_pixels(self):
		"""Write Pixels to Device"""

		prefix = self._start_frame()
		postfix = self._end_frame()

		self.open()

		packet = list()

		packet.extend(prefix)

		for r,g,b,brightness in self.pixels:
			pixel_data = [ brightness | 0xe0, b, g, r ]

			packet.extend(pixel_data)

		packet.extend(postfix)

		self.xfer(packet)

		self.close()

	def brightness(self, pixel, brightness):
		"""Set Brightness of LED"""

		self.pixels[pixel][3] = self._brightness_check(brightness)

	def color(self, pixel, r=None, g=None, b=None, color=None):
		"""Set Color of Pixel"""

		if r is not None:
			self.pixels[pixel][0] = self._color_check(r)
		if g is not None:
			self.pixels[pixel][1] = self._color_check(g)
		if b is not None:
			self.pixels[pixel][2] = self._color_check(b)

		if color is not None:
			r, g, b = color

			self.pixels[pixel][0] = self._color_check(r)
			self.pixels[pixel][1] = self._color_check(g)
			self.pixels[pixel][2] = self._color_check(b)

	def set_pixel(self, pixel, r, g, b, brightness):
		"""Set Pixel"""

		self.color(pixel, r=r, g=g, b=b)
		self.brightness(pixel, brightness)

	def set_all(self, r, g, b, brightness):
		"""Set all Pixels to Given Color and Brightness"""

		for pixel in range(len(self.pixels)):
			self.set_pixel(pixel, r, g, b, brightness)

class SparkfunLumenati3x3(SparkfunLumenati):
	"""Sparkfun Lumenati 3x3 LED Module"""

	state = False

	def __init__(self, name, description, bus=0, device=0, bus_speed=500000, config_section=None):
		"""Init Sparkfun Lumenati 3x3 LED Module Instance"""

		super(ProductInfo,self).__init__(
			"COM-14360",
			"Sparkfun Lumenati 3x3 LED Panel",
			"https://www.sparkfun.com/products/retired/14360?_gl=1*hzi0go*_ga*MjEzMjQ1MDQzMy4xNjk4MTg3Mjkw*_ga_T369JS7J9N*MTcwMDEwMTU1OS41LjEuMTcwMDEwMzAyMC42MC4wLjA.",
			"https://learn.sparkfun.com/tutorials/lumenati-hookup-guide/all")

		super(SparkfunLumenati,self).__init__(
			pixels=9,
			bus=bus,
			device=device,
			bus_speed=bus_speed,
			config_section=config_section)

		self.name = name
		self.description = description

		if config_section is not None:
			self.config(config_section)

	def config(self,config_section):
		"""Config Device from INI Section"""

		if "name" in config_section:
			self.name = config_section["name"]

		if "description" in config_section:
			self.description = config_section["description"]

		if "color" in config_section:
			colorspec = config_section["color"]

			rs,gs,bs,ibs = self.get_specs_sv(colorspec)

			r = int(rs)
			g = int(gs)
			b = int(bs)
			brightness = int(ibs)

			self.set_all(r, g, b, brightness)

	def set_row(self, row, color, brightness = 8):
		"""Set Row Color"""

		for pixel in range(3):
			self.set_pixel((row * 3) + pixel, color=color)
			self.set_brightness((row * 3) + pixel, brightness)

	def on(self):
		"""Turn Panel On"""

		self.set_all(255,255,255, 8)

		self.write_pixels()

		self.state = True


	def off(self):
		"""Turn Panel Off"""

		self.set_all(0,0,0,0)
		self.write_pixels()

		self.state = False

	@property
	def is_on(self):
		"""Is Panel Active"""

		return self.state

	def test_module(self):
		"""Test Function"""

		self.set_all(0,0,0,0)

		self.write_pixels()

		self.set_row(0, self.red)
		self.set_row(1, self.white)
		self.set_row(2, self.blue)

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

def sparkfun_build_out(robot):
	"""Run through elements, pick out Sparkfun Hardware and build them out"""

	built_elements = list()

	my_devices = list(["sparkfun_lumenati3x3", "sparkfun_motor_driver"])

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
						if device_type == my_devices[0]:
							panel = SparkfunLumenati3x3(section_label, description, config_section=section)

							built_elements.append(panel)

							robot.add(panel)
						elif device_type == mydevices[1]:
							mc = SparkfunMotorDriver(section_label, description, config_section=section)

							built_elements.append(mc)

							robot.add(mc)
					else:
						pass
				else:
					DbgMsg("'hardware' not in section")
			else:
				DbgMsg(f"Attempt to get element section, {section_label}, from robot INI failed")

	return built_elements

def sparkfun_module_tests():
	"""Test Function"""

	pass

#
# Main Loop
#

if __name__ == "__main__":
	CmdLineMode(True)

	Msg("This module is not intended to be executed by itself")
