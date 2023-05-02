from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from stitchtoon.services import postprocess_run
from stitchtoon.services.global_logger import logFunc


class PostProcessThread(QThread):
    started = Signal()
    finished = Signal(int)
    console = Signal(str, str)

    def __init__(self, cmd: str, args: str, parent=None):
        super().__init__(parent)
        self.cmd = cmd
        self.args = args

    @logFunc(inclass=True)
    def run(self):
        self.started.emit()
        try:
            return_code = postprocess_run(self.cmd, self.args, self.console_print)
        except Exception as e:
            self.console_print(f"ERROR: {e}", "error")
        else:
            self.finished.emit(return_code)

    def console_print(self, msg, type="normal"):
        self.console.emit(msg, type)

    def stop(self):
        self.terminate()
