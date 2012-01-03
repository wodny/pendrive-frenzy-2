#    Copyright 2011  Marcin Szewczyk <Marcin.Szewczyk@wodny.org>
#
#    This file is part of pendrive-frenzy.
#
#    Pendrive-frenzy is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Pendrive-frenzy is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with pendrive-frenzy.  If not, see <http://www.gnu.org/licenses/>.


import ConfigParser
import os.path


class ConfigException(Exception):
    pass


class Config:
    def __init__(self, path):
        self.path = path

        self.parser = ConfigParser.SafeConfigParser()
        self.parser.read(path)

        # Validation
        generaloptions = (
            "mode",
            "description",
            "copycommand",
            "copycommand_params",
            "postscript"
        )
        for i in generaloptions:
            value = self.parser.get("general", i)
            self.__dict__[i] = value

        self.postscript = self.prefix_with_basedir(self.postscript)

        if self.mode not in ("copy-only", "create-mbr"):
            raise ConfigException("Invalid mode")

        self.partitions = [
            int(part)
            for part
            in self.parser.get("general", "partitions").split(',')
        ]
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
        realpath = os.path.realpath(self.path)
        dirname = os.path.dirname(realpath)
        return os.path.join(dirname, "scripts", path)

    def get_partdata_spec(self, p):
        p = str(p)
        realpath = os.path.realpath(self.path)
        dirname = os.path.dirname(realpath)
        path = os.path.join(dirname, "partitions", p)
        if os.path.isdir(path):
            return ("{0}/".format(path), "copy-files")
        else:
            return (path, "copy-image")
