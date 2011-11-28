class MasterEvent:
    pass

class Quit(MasterEvent):
    def handle(self, dispatch):
        print(_("Master quit"))
        dispatch.work = False
