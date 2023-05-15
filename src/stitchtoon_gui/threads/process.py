# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.


from PySide6.QtCore import QThread
from PySide6.QtCore import Signal
from stitchtoon import process
from stitchtoon.services.global_logger import logFunc
from stitchtoon.utils.errors import EmptyImageDir
from stitchtoon.utils.errors import SizeLimitError


class ProcessThread(QThread):
    finished = Signal(bool)
    exceptionRaised = Signal(Exception)

    def __init__(self, params, parent=None):
        super().__init__(parent)
        self.params = params

    @logFunc(inclass=True)
    def run(self):
        success = False
        try:
            process(**self.params)
        except (EmptyImageDir, SizeLimitError, FileNotFoundError) as e:
            self.exceptionRaised.emit(str(e))
        except Exception as e:
            self.exceptionRaised.emit(str(e))
        else:
            success = True
        finally:
            self.finished.emit(success)

    def stop(self):
        self.terminate()
