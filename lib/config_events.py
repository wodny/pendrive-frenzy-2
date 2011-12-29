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
from lib.config import Config, ConfigException
import gui_updates
import logging

class ConfigEvent:
    pass

class ReadConfig(ConfigEvent):
    def __init__(self, path):
        self.path = path

    def handle(self, dispatch):
        try:
            logging.info(_("Loading configuration from file {0}...".format(self.path)))
            config = Config(self.path)
            logging.info(_("Configuration loaded."))
            dispatch.config = config
            description = config.description
            dispatch.updates_in.put(gui_updates.StatusBarUpdate(_("Configuration loaded.")))
            dispatch.updates_in.put(gui_updates.InfoBarUpdate(description))
        except (ConfigParser.Error, ValueError, ConfigException) as e:
            logging.error(_("Configuration parsing error: {0}".format(e)))
            dispatch.updates_in.put(gui_updates.StatusBarUpdate(_("Configuration parsing error.")))
            dispatch.updates_in.put(gui_updates.InfoBarUpdate(""))
