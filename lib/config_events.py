import ConfigParser
from lib.config import Config
import gui_updates

class ConfigEvent:
    pass

class ReadConfig(ConfigEvent):
    def __init__(self, path):
        self.path = path

    def handle(self, dispatch):
        try:
            config = Config(self.path)
            loaded_msg = _("Configuration loaded ({0}).".format(self.path))
            print(loaded_msg)
            dispatch.config = config
            description = config.get_description()
            dispatch.updates_in.put(gui_updates.StatusBarUpdate(loaded_msg))
            dispatch.updates_in.put(gui_updates.InfoBarUpdate(description))
        except (ConfigParser.Error, ValueError) as e:
            print(_("Configuration parsing error."))
            print(e)
            dispatch.updates_in.put(gui_updates.StatusBarUpdate(_("Configuration parsing error.")))
            dispatch.updates_in.put(gui_updates.InfoBarUpdate(""))
