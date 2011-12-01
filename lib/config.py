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

        parts = self.parser.getint("general", "partitions")

        for p in range(1, parts+1):
            section = "partition_{0}".format(p)
            self.parser.getint(section, "start")
            self.parser.getint(section, "size")
            self.parser.get(section, "fstype")
            self.parser.getboolean(section, "boot")

    def get_description(self):
        return self.parser.get("general", "description")
