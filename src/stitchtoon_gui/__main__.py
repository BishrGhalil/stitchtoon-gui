import gc
import logging
import sys

from .mainwindow import MainWindow
from .settings import settings
from PySide6.QtWidgets import QApplication


logging.basicConfig()


def exit_handler(app):
    settings.sync()
    logging.log(logging.INFO, "Exiting app")
    gc.collect()
    app.quit()


def main():
    QApplication.setDesktopSettingsAware(True)
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(True)
    app.setQuitLockEnabled(False)
    widget = MainWindow()
    widget.ui.exitButton.clicked.connect(lambda: exit_handler(app))
    app.aboutToQuit.connect(lambda: exit_handler)
    widget.show()
    return_code = app.exec()
    sys.exit(return_code)


if __name__ == "__main__":
    main()
