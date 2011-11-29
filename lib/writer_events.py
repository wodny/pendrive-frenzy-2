from gui_updates import StatusUpdate

class WriterEvent:
    pass

class StatusUpdate(WriterEvent):
    def __init__(self, pendrive, status_code, status_text):
        self.pendrive = pendrive
        self.status_code = status_code
        self.status_text = status_text

    def handle(self, dispatch):
        dispatch.updates_in.send(
            StatusUpdate(
                self.pendrive,
                self.status_code,
                self.status_text
            )
        )
