# Imports
import configparser
import re
import os
import hashlib


class Game(object):
    """ Game object stores game details read from consol """

    def __init__(self, desktop_string, logger):
        # Call parent's constructor
        super(Game, self).__init__()

        # Parse desktop string
        self.config = configparser.ConfigParser(allow_no_value=True)
        self.config.read_string(desktop_string)

        # Get id and title
        self.id = self.config["X-CLOVER Game"]["code"]
        self.title = self.config["Desktop Entry"]["Name"]

        # Get ROM path
        self.rom = re.search("(?<=-rom ).*.sfrom",
                             self.config["Desktop Entry"]["exec"]).group(0)

        # Get RAM path
        self.ram = self.config["Desktop Entry"]["path"] + "/cartridge.sram"
        self.ram_hash = self.config["Desktop Entry"]["path"] + \
            "/cartridge.sram.hash"

        # Save logger
        self.logger = logger

        # with open('example.ini', 'w') as configfile:
        #   self.config.write(configfile)

    """ Get title of the game """

    def getTitle(self):
        return self.title

    """ Get list of files on console related to game """

    def getConsoleFiles(self):
        # Return rom, ram and ram hasd path
        return [self.rom, self.ram, self.ram_hash]

    """ Save console files to computer """

    def saveConsoleFiles(self, dir, flist):
        # Create game folder if does not exist
        if not os.path.isdir(dir + "/" + self.id):
            os.mkdir(dir + "/" + self.id)

        # Save desktop file
        with open(dir + "/" + self.id + "/desktop.ini", "w", encoding="utf-8") as f:
            self.config.write(f)

        # Save rom
        if len(flist[0]) > 0:
            with open(dir + "/" + self.id + "/rom.sfrom", "wb") as f:
                f.write(flist[0])

        # Save ram
        if len(flist[1]) > 0:
            with open(dir + "/" + self.id + "/ram.sram", "wb") as f:
                f.write(flist[1])
            with open(dir + "/" + self.id + "/ram.srm", "wb") as f:
                f.write(flist[1][0:-20])

        # Save rom
        if len(flist[2]) > 0:
            with open(dir + "/" + self.id + "/ram.sram.hash", "wb") as f:
                f.write(flist[2])

            # Check hash calculation
            if len(flist[1]) > 0:
                # Caclulate hash
                h = hashlib.sha1(flist[1][0:-20])

                # Verify hash
                if h.digest() != flist[2]:
                    self.logger.error("hash verify failed for game '%s'", self.id)

                # Write hash to file
                with open(dir + "/" + self.id + "/ram.srm.hash", "wb") as f:
                    f.write(h.digest())


    """ String representation of the object """

    def __repr__(self):
        return "Game: '" + self.title + "'" + " rom: '" + self.rom + "'"
