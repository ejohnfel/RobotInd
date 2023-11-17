#
# Pimoroni Technology Module
#

import py_helper as ph
from py_helper import DebugMode, CmdLineMode, DbgMsg, Msg, Taggable

#
# GPIO Zero Stuff
#
import gpiozero as gpz
from gpiozero import *

#
# Constants
#

#
# Variables
#

#
# Classes
#

class PimoroniLipoShim(SimpleGPIODevice):
	"""Pimoroni Lipo Shim"""

	def __init__(self, name, description, config_section=None):
		"""Init Lipo Shim Instance"""

		# GPIO 4, PIN 7 not sure what this is in BCM
		super().__init__(name, description, 7, False, True, config_section=config_section)

		if config_section is not None:
			self.config(config_section)

	def config(self, config_section):
		"""Config Instance From INI Section"""

		pass

#
# Functions
#


def pimoroni_module_tests():
	"""Test Function"""

	pass

#
# Main Loop
#

if __name__ == "__main__":
	CmdLineMode(True)

	Msg("This module is not intended to be executed by itself")
