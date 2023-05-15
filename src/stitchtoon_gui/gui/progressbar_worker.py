# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.

from PySide6.QtCore import QObject
from PySide6.QtCore import Signal


class ProgressWorker(QObject):
    started = Signal()
    finished = Signal()
    valueChanged = Signal(int)
    textChanged = Signal(str)

    def __init__(self, prefix="", size=100, parent=None):
        super().__init__(parent)
        self.prefix = prefix
        self.size = size
        self._value = 0
        self._precent = size

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if self._value == value:
            return
        self._value = value

    def update(self, value, msg=""):
        self.value = value
        self.valueChanged.emit(self._value)
        if msg:
            self.prefix = msg
            self.textChanged.emit(self.prefix)

    def start(self):
        self.started.emit()
        self.update(0, "started")

    def finish(self):
        self.finished.emit()
        self.update(self.size, "completed")
