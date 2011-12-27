import ConfigParser
import os.path

class ConfigException(Exception):
    pass

class Config:
    def __init__(self, path):
        self.path = path

        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(path)
        sections = self.parser.sections()
        
        # Validation
        for i in ("mode", "description", "copycommand", "copycommand_params", "postscript"):
            value = self.parser.get("general", i)
            self.__dict__[i] = value

        self.postscript = self.prefix_with_basedir(self.postscript)

        if self.mode not in ("copy-only", "create-mbr"):
            raise ConfigException("Invalid mode")

        self.partitions = [ int(part) for part in self.parser.get("general", "partitions").split(',') ]
        self.partitions.sort()

        self.partspecs = dict()

        for p in self.partitions:
            section = "partition_{0}".format(p)
            self.partspecs[p] = dict()
            self.partspecs[p]["id"] = p
            self.partspecs[p]["start"] = self.parser.getint(section, "start")
            self.partspecs[p]["size"] = self.parser.getint(section, "size")
            self.partspecs[p]["type"] = self.parser.get(section, "type")
            self.partspecs[p]["fstype"] = self.parser.get(section, "fstype")
            self.partspecs[p]["label"] = self.parser.get(section, "label")
            self.partspecs[p]["boot"] = self.parser.getboolean(section, "boot")
            (self.partspecs[p]["path"], self.partspecs[p]["method"]) = \
                self.get_partdata_spec(p)
            self.partspecs[p]["postscript"] = self.prefix_with_basedir(
                self.parser.get(section, "postscript")
            )

    def prefix_with_basedir(self, path):
        if not path:
            return ""
        abspath = os.path.abspath(self.path)
        dirname = os.path.dirname(abspath)
        return os.path.join(dirname, "scripts", path)

    def get_partdata_spec(self, p):
        p = str(p)
        abspath = os.path.abspath(self.path)
        dirname = os.path.dirname(abspath)
        path = os.path.join(dirname, "partitions", p)
        if os.path.isdir(path):
            return ("{0}/".format(path), "copy-files")
        else:
            return (path, "copy-image")
