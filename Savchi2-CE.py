# Imports
import logging
import logging.config
import json
import sys
import time
from ftplib import FTP

# Defines
CONFIG_LOG  = "logging.conf"
CONFIG_FILE = "config.conf"
CONFIG_FILE_KEYS = ["IP", "user", "pwd", "period", "games", ]

# Create logger based on config
logging.config.fileConfig(CONFIG_LOG)
logger = logging.getLogger("Savchi2 CE")


# Welcome message
logger.info("Savchi2 CE started")

# Try to load configuraiotn
try:
	# Try to open config file
	logger.debug("Opening config file %s", CONFIG_FILE)
	with open(CONFIG_FILE, "r") as  f:
		# Load config from json
		logger.debug("Loading config file")
		conf = json.load(f)

# Config could not be loaded, create default config
except:
	logger.debug("Config file open failed, creating default config")
	conf = {}

# Check for correct config file
if list(conf.keys()) != CONFIG_FILE_KEYS:
	conf = {
		"IP": "169.254.13.37",
		"user": "root",
		"pwd": "clover",
		"period": 1.0,
		"games": "/var/games",
		}

	# Save new config file
	with open(CONFIG_FILE, "w") as  f:
		# Load config from json
		logger.debug("Default config file created")
		json.dump(conf, f)

# Do main loop
logger.info("Connecting to FTP server through IP %s", conf["IP"])
while True:
	# Connect to FTP server
	try:
		logger.debug("Connecting to FTP server through IP %s", conf["IP"])
		with FTP(conf["IP"]) as ftp:

			# Log in to FTP server
			logger.debug("Logging in to FTP server as user '%s' with password '%s'", conf["user"], conf["pwd"])
			ftp.login(user=conf["user"], passwd=conf["pwd"])
			logger.info("Connection succeeded")

			# Get game catalog
			logger.debug("Reading game catalog")
			games = ftp.nlst(conf["games"])

			# Read game details
			for game in games[0:2]:

				# Read game data
				data = ""
				def cb(d):
					global data
					data = data + str(d)
				ftp.retrbinary("RETR " + conf["games"] + "/" + 
								game + "/" + game + ".desktop", cb)
				print("%s: %s" % (game, data))
			break
	
	# Exit on interruption
	except KeyboardInterrupt:
		break

	# Retry on other error - exceptions to catch should be defined
	except Exception as e:
		raise e
		logger.debug("Operation failed, retry in %.1fs", conf["period"])
		
		# Wait
		try:
			time.sleep(conf["period"])
		
		# Exit on interruption
		except KeyboardInterrupt:
			break

logger.info("Terminated, exiting")
