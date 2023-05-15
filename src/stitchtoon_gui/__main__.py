# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.

import argparse
import gc
import sys
from pathlib import Path

from . import __version__
from .gui.mainwindow import MainWindow
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication


def exit_handler(*to_exit):
    for i in to_exit:
        i.exit_handler()
    gc.collect()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "--reset", action="store_true", help="Resets settings to default", default=False
    )
    parser.add_argument(
        "--debug", action="store_true", help="Runs in debug mode", default=False
    )
    args = parser.parse_args()

    if args.reset:
        from .utils.settings import settings

        settings.reset()

    if args.debug:
        import logging

        from stitchtoon.services.global_logger import Logger
        from stitchtoon.services.global_logger import get_logger

        global Logger
        if sys.platform.startswith("win"):
            home = Path.home() / "Desktop"
        else:
            home = Path.home()
        Logger = get_logger(logging.DEBUG, str(home / "STITCHTOON_LOG.log"))

    QApplication.setDesktopSettingsAware(True)
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    app.setQuitLockEnabled(False)
    widget = MainWindow()
    app.aboutToQuit.connect(lambda: exit_handler(widget))
    widget.show()
    return_code = app.exec()
    sys.exit(return_code)


if __name__ == "__main__":
    main()
