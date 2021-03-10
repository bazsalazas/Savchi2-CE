# Imports
import logging
import logging.config
import configparser
import os
import time
from ftplib import FTP

from game import Game

# Defines
LOGGING_CONFIG = "logging.ini"
CONFIG_FILE = "config.ini"

# Create logger based on config
logging.config.fileConfig(LOGGING_CONFIG)
logger = logging.getLogger("Savchi2 CE")

# Welcome message
logger.info("Savchi2 CE started")

# Load configuration
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

# Create game folder if does not exist
if not os.path.isdir("games"):
    os.mkdir("games")

# Do main loop
logger.info("Connecting to FTP server through IP %s", config["FTP"]["IP"])
while True:
    # Connect to FTP server
    try:
        logger.debug("Connecting to FTP server through IP %s",
                     config["FTP"]["IP"])
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
                # Init buffer
                data = bytes()

                # Data read callback
                def cb(d):
                    global data
                    data = data + d
                # Read game catalog
                ftp.retrbinary("RETR " + config["Games"]["catalog"].format(
                    path=config["Games"]["path"], ID=gid), cb)

                # Create game object
                game = Game(data.decode("utf-8"), logger)
                games.append(game)
                logger.info("Game found: '%s'", game.getTitle())

                # Read game files
                fd = []
                for f in game.getConsoleFiles():
                    # Clear buffer
                    data = bytes()

                    # Check if game file exists
                    if len(ftp.nlst(f)) == 1:
                        # Read game file
                        logger.debug("Download file: '%s'", f)
                        ftp.retrbinary("RETR " + f, cb)

                    # Add to results
                    fd.append(data)

                # Save game files
                logger.debug("Save game files")
                game.saveConsoleFiles("games", fd)
            break

    # Exit on interruption
    except KeyboardInterrupt:
        break

    # Retry on other error - exceptions to catch should be defined
    except Exception as e:
        raise e
        logger.debug("Operation failed, retry in %.1fs",
                     config["Settings"]["poll peroid"])

        # Wait
        try:
            time.sleep(config["Settings"]["poll peroid"])

        # Exit on interruption
        except KeyboardInterrupt:
            break

logger.info("Terminated, exiting")
