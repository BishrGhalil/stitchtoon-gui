import gc
import os
import shlex
from pathlib import Path

from .constants import DEFAULT_THEME
from .constants import OUTPUT_SUFFIX
from .constants import SUPPORTS_LOSSY_QUALITY
from .postprocess import PostProcessThread
from .process import ProcessThread
from .progressbar_worker import ProgressWorker
from .settings import settings
from PySide6.QtCore import QCoreApplication
from PySide6.QtCore import QFile
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMainWindow
from qt_material import QtStyleTools
from qt_material import apply_stylesheet
from stitchtoon.services.global_logger import logFunc


QTMATERIAL_PRIMARYTEXTCOLOR = os.environ.get("QTMATERIAL_PRIMARYTEXTCOLOR")
QTMATERIAL_SECONDARYTEXTCOLOR = os.environ.get("QTMATERIAL_SECONDARYTEXTCOLOR")
CUSTOM_CSS = os.path.join(os.path.dirname(__file__), "custom.css")


class MainWindow(QMainWindow, QtStyleTools):
    def __init__(self, parent=None):
        super().__init__()
        self.theme = DEFAULT_THEME
        self.profile = settings.get_profile()
        self.profileName = self.profile["name"]
        self.progress = ProgressWorker()

        self.ui = self.load_ui()
        self.configure_ui()
        self.connect()

    def load_ui(self) -> None:
        """Loads UI File"""

        loader = QUiLoader()
        path = Path(__file__).resolve().parent / "layout.ui"
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        mainwindow_ui = loader.load(ui_file, self)
        ui_file.close()
        return mainwindow_ui

    def configure_ui(self) -> None:
        """Sets Widgets values against saved settings"""

        # Stitch
        self.ui = self.load_ui()
        self.load_profile(self.profile)
        self.show_advanced_options(self.ui.advancedOptions.isChecked())
        self.show_lossy_quality(self.ui.outputFormat.currentText())
        self.show_width_enforcement(self.ui.widthEnforcement.currentText())
        self.ui.lossyQuality.setText(f"{self.ui.lossyQualitySlider.value()}%")
        # Settings And Post Process
        self.enable_postprocess(self.ui.enablePostProcess.isChecked())
        self.ui.profileName.setText(self.ui.settingsProfiles.currentText())
        self.change_theme(self.theme)

    def connect(self) -> None:
        """Connects Signals and Slots"""

        self.ui.outputFormat.currentTextChanged.connect(self.show_lossy_quality)
        self.ui.themeComboBox.currentTextChanged.connect(self.change_theme)
        self.ui.advancedOptions.stateChanged.connect(self.show_advanced_options)
        self.ui.widthEnforcement.currentTextChanged.connect(self.show_width_enforcement)
        self.progress.valueChanged.connect(self.ui.progressBar.setValue)
        self.ui.start.clicked.connect(self.start)
        self.ui.addProfile.clicked.connect(
            lambda: self.add_profile(self.ui.profileName.text())
        )
        self.progress.textChanged.connect(
            lambda x: self.ui.progressBar.setFormat(f"{x} %p%")
        )
        self.ui.input.textChanged.connect(
            lambda input: self.ui.output.setText(input + OUTPUT_SUFFIX if input else "")
        )
        self.ui.lossyQualitySlider.valueChanged.connect(
            lambda x: self.ui.lossyQuality.setText(f"{x}%")
        )
        self.ui.profile.currentTextChanged.connect(
            lambda x: self.load_profile(settings.get_profile(x))
        )
        self.ui.inputBrowse.clicked.connect(
            lambda: self.ui.input.setText(self.browse_dialog(self.ui.input.text()))
        )
        self.ui.outputBrowse.clicked.connect(
            lambda: self.ui.output.setText(self.browse_dialog(self.ui.output.text()))
        )
        self.ui.postProcessBrowse.clicked.connect(
            lambda: self.ui.postProcessScript.setText(
                self.browse_dialog(self.ui.postProcessScript.text())
            )
        )
        self.ui.enablePostProcess.stateChanged.connect(
            lambda x: self.enable_postprocess(x)
        )

    @logFunc(inclass=True)
    def load_profile(self, profile: dict[str:any]) -> None:
        """Sets Widgets values according to a profile"""

        for pn in settings["profiles"].keys():
            self.ui.profile.clear()
            self.ui.profile.addItem(pn)
            self.ui.settingsProfiles.addItem(pn)

        self.ui.settingsProfiles.setCurrentText(profile["name"])
        self.ui.profile.setCurrentText(profile["name"])
        self.ui.outputFormat.setCurrentText(profile["outputFormat"])
        self.ui.widthEnforcement.setCurrentText(profile["widthEnforcement"])
        self.ui.detectionType.setCurrentText(profile["detectionType"])
        self.ui.lossyQualitySlider.setValue(profile["lossyQuality"])
        self.ui.widthEnforcementSpinBox.setValue(profile["widthEnforcementFixedValue"])
        self.ui.splitHeight.setValue(profile["splitHeight"])
        self.ui.sensitivity.setValue(profile["sensitivity"])
        self.ui.lineSteps.setValue(profile["lineSteps"])
        self.ui.ignorablePixels.setValue(profile["ignorablePixels"])
        self.ui.batchMode.setChecked(profile["batchMode"])
        self.ui.exportArchive.setChecked(profile["exportArchive"])

    @logFunc(inclass=True)
    def make_profile(self, name: str) -> dict[str, any]:
        """Creates a profile"""

        profile = {}
        profile["name"] = name
        profile["outputFormat"] = self.ui.outputFormat.currentText()
        profile["widthEnforcement"] = self.ui.widthEnforcement.currentText()
        profile["detectionType"] = self.ui.detectionType.currentText()
        profile["lossyQuality"] = self.ui.lossyQualitySlider.value()
        profile["widthEnforcementFixedValue"] = self.ui.widthEnforcementSpinBox.value()
        profile["splitHeight"] = self.ui.splitHeight.value()
        profile["sensitivity"] = self.ui.sensitivity.value()
        profile["lineSteps"] = self.ui.lineSteps.value()
        profile["ignorablePixels"] = self.ui.ignorablePixels.value()
        profile["batchMode"] = self.ui.batchMode.isChecked()
        profile["exportArchive"] = self.ui.exportArchive.isChecked()

        return profile

    def add_profile(self, name: str) -> None:
        if settings.get_profile(name):
            return
        profile = self.make_profile(name)
        settings["profiles"] = settings["profiles"].update({name: profile})
        self.load_profile(profile)

    def show(self):
        self.ui.show()

    @logFunc(inclass=True)
    def show_advanced_options(self, state):
        self.ui.advancedOptionsFrame.setVisible(state)
        size = self.maximumSize() if state else self.minimumSize()
        self.ui.resize(size)

    @logFunc(inclass=True)
    def show_lossy_quality(self, format):
        state = False
        if format.lower() in SUPPORTS_LOSSY_QUALITY:
            state = True
        self.ui.lossyQualityWidget.setVisible(state)

    @logFunc(inclass=True)
    def show_width_enforcement(self, method):
        state = True
        if method.lower() in ("none", "auto"):
            state = False
            self.ui.widthEnforcementSpinBox.setValue(0)
        self.ui.widthEnforcementSpinBox.setVisible(state)

    @logFunc(inclass=True)
    def change_theme(self, theme):
        theme = theme.lower().replace(" ", "_")
        if "dark" in theme:
            invert_secondary = False
        elif "light" in theme:
            invert_secondary = True

        self.theme = theme
        settings["theme"] == theme
        apply_stylesheet(
            self.ui,
            theme + ".xml",
            invert_secondary=invert_secondary,
            css_file=CUSTOM_CSS,
        )

    @logFunc(inclass=True)
    def enable_postprocess(self, state):
        self.ui.postProcessWidget.setEnabled(state)

    def start(self):
        self.progress.update(0)
        self.status("")
        self.ui.postProcessConsole.clear()

        profile = self.make_profile(currentProfile)
        stitch_params = {
            "detection_type": profile["detectionType"],
            "sensitivity": int(profile["sensitivity"]),
            "custom_width": int(profile["widthEnforcementFixedValue"]),
            "width_enforce": profile["widthEnforcement"],
            "line_steps": int(profile["lineSteps"]),
            "ignorable_pixels": int(profile.get("ignorablePixels")),
        }

        kwargs = {
            "input": self.ui.input.text(),
            "output": self.ui.output.text(),
            "split_height": int(profile["splitHeight"]),
            "output_format": profile["outputFormat"],
            "recursive": bool(profile["batchMode"]),
            "as_archive": bool(profile["exportArchive"]),
            "lossy_quality": int(profile["lossyQuality"]),
            "progress": self.progress,
            "params": stitch_params,
        }

        self.thread = ProcessThread(params=kwargs, console=self.status)
        self.thread.setTerminationEnabled(True)
        self.thread.finished.connect(lambda: self.ui.start.setEnabled(True))
        self.thread.finished.connect(lambda: self.status("Process Finished"))
        self.thread.finished.connect(self.postprocess_start)
        self.ui.start.setEnabled(False)

        try:
            self.thread.start()
        except Exception as e:
            self.status(f"ERROR: {e}", "error")
            raise
        else:
            return 0

    def status(self, msg, type="normal"):
        color = self._get_msg_color(type)
        self.ui.statusbar.setStyleSheet(f"color: {color};")
        self.ui.statusbar.showMessage(msg)

    def _get_msg_color(self, type):
        if not type:
            color = (
                QTMATERIAL_PRIMARYTEXTCOLOR or QTMATERIAL_SECONDARYTEXTCOLOR or "gray"
            )
        elif type.lower() == "error":
            color = "red"
        elif type.lower() == "warning":
            color = "yellow"
        elif type.lower() == "success":
            color = "green"
        else:
            color = (
                QTMATERIAL_PRIMARYTEXTCOLOR or QTMATERIAL_SECONDARYTEXTCOLOR or "gray"
            )

        return color

    def postprocess_console(self, msg, type="normal"):
        color = self._get_msg_color(type)
        self.ui.postProcessConsole.setTextColor(color)
        self.ui.postProcessConsole.append(msg)
        normal = self._get_msg_color("normal")
        self.ui.postProcessConsole.setTextColor(normal)

    def postprocess_start(self):
        if not self.ui.enablePostProcess.isChecked():
            return

        cmd = " ".join(shlex.split(self.ui.postProcessScript.text()))
        args = " ".join(shlex.split(self.ui.postProcessArgs.text()))
        self.postprocess_thread = PostProcessThread(cmd, args)
        self.postprocess_thread.setTerminationEnabled(True)
        self.postprocess_thread.console.connect(self.postprocess_console)
        self.postprocess_thread.started.connect(
            lambda: self.status("Post Process Started")
        )
        self.postprocess_thread.finished.connect(
            lambda x: self.status("Post Process Finished")
            if x == os.EX_OK
            else self.status("Post Process Faild", "error")
        )
        self.postprocess_thread.finished.connect(
            lambda x: self.ui.start.setEnabled(True)
        )
        self.ui.start.setEnabled(False)

        try:
            self.postprocess_thread.start()
        except Exception as e:
            self.status(f"ERROR: {e}")

    def browse_dialog(self, startPath=None):
        if not startPath:
            startPath = str(Path.home())
        return QFileDialog.getExistingDirectory(
            self, "Select Directory", startPath, QFileDialog.ShowDirsOnly
        )
