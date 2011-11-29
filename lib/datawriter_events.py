import gui_updates

class DataWriterEvent:
    pass

class StatusUpdate(DataWriterEvent):
    def __init__(self, pendrive, status_code, status_text):
        self.pendrive = pendrive
        self.status_code = status_code
        self.status_text = status_text

    def handle(self, dispatch):
        dispatch.updates_in.send(
            gui_updates.StatusUpdate(
                self.pendrive,
                self.status_code,
                self.status_text
            )
        )
