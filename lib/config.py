import ConfigParser

class Config:
    def __init__(self, path):
        self.path = path

        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(path)
        sections = self.parser.sections()
        
        # Validation
        for i in ("mode", "description", "copycommand", "copycommand_params"):
            self.parser.get("general", i)

        # TODO: get_description incompatible with this
        self.mode = self.parser.get("general", "mode")

        self.partitions = set( int(part) for part in self.parser.get("general", "partitions").split(',') )

        for p in self.partitions:
            section = "partition_{0}".format(p)
            self.parser.getint(section, "start")
            self.parser.getint(section, "size")
            self.parser.get(section, "fstype")
            self.parser.getboolean(section, "boot")

    def get_description(self):
        return self.parser.get("general", "description")
