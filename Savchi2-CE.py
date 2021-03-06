# Imports
import logging
import logging.config
import configparser
import time
from ftplib import FTP

from game import Game

# Defines
LOGGING_CONFIG  = "logging.ini"
CONFIG_FILE = "config.ini"


# Create logger based on config
logging.config.fileConfig(LOGGING_CONFIG)
logger = logging.getLogger("Savchi2 CE")


# Welcome message
logger.info("Savchi2 CE started")

# Load configuration
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Do main loop
logger.info("Connecting to FTP server through IP %s", config["FTP"]["IP"])
while True:
	# Connect to FTP server
	try:
		logger.debug("Connecting to FTP server through IP %s", config["FTP"]["IP"])
		with FTP(config["FTP"]["IP"]) as ftp:

			# Log in to FTP server
			logger.debug("Logging in to FTP server as user '%s' with password '%s'",
						 config["FTP"]["user"], config["FTP"]["pwd"])
			ftp.login(user=config["FTP"]["user"], passwd=config["FTP"]["pwd"])
			logger.info("Connection succeeded")

			# Get game ids
			logger.debug("Reading game catalog")
			gids = ftp.nlst(config["Games"]["path"])

			# Read game details
			games = []
			for gid in gids:

				# Read game ctalog
				catalog = bytes()
				def cb(d):
					global catalog
					catalog = catalog + d
				ftp.retrbinary("RETR " + config["Games"]["catalog"].format(
								path=config["Games"]["path"], ID=gid), cb)

				# Create game object
				games.append(Game(catalog.decode("utf-8")))
				logger.debug("Game found: '%s'", games[-1].getTitle())
			break
	
	# Exit on interruption
	except KeyboardInterrupt:
		break

	# Retry on other error - exceptions to catch should be defined
	except Exception as e:
		raise e
		logger.debug("Operation failed, retry in %.1fs", config["Settings"]["poll peroid"])
		
		# Wait
		try:
			time.sleep(config["Settings"]["poll peroid"])
		
		# Exit on interruption
		except KeyboardInterrupt:
			break

logger.info("Terminated, exiting")
