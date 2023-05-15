# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.

from .. import __version__
from PySide6.QtCore import QThread
from PySide6.QtCore import Signal


class UpdateCheckThread(QThread):
    updateAvailable = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            from ..utils.version_check import get_repo_version
            from ..utils.version_check import parse_version

            remote_version = get_repo_version(
                "stitchtoon-gui",
                "BishrGhalil",
                default=("", "0.0.0"),
            )
            if parse_version(str(remote_version[1])) > parse_version(str(__version__)):
                self.updateAvailable.emit(
                    remote_version[1],
                    "https://github.com/BishrGhalil/stitchtoon-gui/releases",
                )
        except Exception:
            raise
        else:
            return 0

    def stop(self):
        self.terminate()
