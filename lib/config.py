import ConfigParser

class ConfigException(Exception):
    pass

class Config:
    def __init__(self, path):
        self.path = path

        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(path)
        sections = self.parser.sections()
        
        # Validation
        for i in ("mode", "description", "copycommand", "copycommand_params"):
            value = self.parser.get("general", i)
            self.__dict__[i] = value

        if self.mode not in ("copy-only", "create-mbr"):
            raise ConfigException("Invalid mode")

        self.partitions = set( int(part) for part in self.parser.get("general", "partitions").split(',') )

        self.partspec = dict()

        for p in self.partitions:
            section = "partition_{0}".format(p)
            self.partspec[p] = dict()
            self.partspec[p]["start"] = self.parser.getint(section, "start")
            self.partspec[p]["size"] = self.parser.getint(section, "size")
            self.partspec[p]["type"] = self.parser.get(section, "type")
            self.partspec[p]["fstype"] = self.parser.get(section, "fstype")
            self.partspec[p]["label"] = self.parser.get(section, "label")
            self.partspec[p]["boot"] = self.parser.getboolean(section, "boot")
