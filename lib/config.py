import ConfigParser

class Config:
    def __init__(self, path):
        self.path = path

        parser = ConfigParser.SafeConfigParser()
        parser.read(path)
        sections = parser.sections()
        
        # Validation
        for i in ("mode", "description", "copycommand", "copycommand_params"):
            parser.get("general", i)

        parts = parser.getint("general", "partitions")

        for p in range(1, parts+1):
            section = "partition_{0}".format(p)
            parser.getint(section, "start")
            parser.getint(section, "size")
            parser.get(section, "fstype")
            parser.getboolean(section, "boot")
