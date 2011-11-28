class GUIEvent:
    pass

class Quit(GUIEvent):
    def handle(self, dispatch):
        print(_("GUI quit"))
        dispatch.work = False
