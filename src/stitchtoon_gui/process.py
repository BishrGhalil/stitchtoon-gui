from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from stitchtoon import process
from stitchtoon.services.global_logger import logFunc


class ProcessThread(QThread):
    finished = Signal()

    def __init__(self, params, console, parent=None):
        super().__init__(parent)
        self.params = params
        self.console = console

    @logFunc(inclass=True)
    def run(self):
        try:
            process(**self.params)
        except Exception as e:
            self.console(f"ERROR: {e}", "error")
            raise
        else:
            return 0

        self.finished.emit()

    def stop(self):
        self.terminate()
