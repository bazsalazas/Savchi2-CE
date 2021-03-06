# Imports
import configparser
import re

# Class for games
class Game(object):
	""" Game object stores game details read from consol """
	def __init__(self, desktop_string):
		# Call parent's constructor
		super(Game, self).__init__()

		# Parse desktop string
		self.config = configparser.ConfigParser(allow_no_value=True)
		self.config.read_string(desktop_string)

		# Get title
		self.title = self.config["Desktop Entry"]["Name"]
		
		# Get ROM path
		self.rom = re.search("(?<=-rom ).*.sfrom", self.config["Desktop Entry"]["exec"]).group(0)

		#with open('example.ini', 'w') as configfile:
		#	self.config.write(configfile)	

	""" String representation of the object """
	def __repr__(self):
		return "Game: '" + self.title + "'" + " rom: '" + self.rom + "'"
