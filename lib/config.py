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

        self.partspecs = dict()

        for p in self.partitions:
            section = "partition_{0}".format(p)
            self.partspecs[p] = dict()
            self.partspecs[p]["start"] = self.parser.getint(section, "start")
            self.partspecs[p]["size"] = self.parser.getint(section, "size")
            self.partspecs[p]["type"] = self.parser.get(section, "type")
            self.partspecs[p]["fstype"] = self.parser.get(section, "fstype")
            self.partspecs[p]["label"] = self.parser.get(section, "label")
            self.partspecs[p]["boot"] = self.parser.getboolean(section, "boot")
