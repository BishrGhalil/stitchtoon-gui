# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.


import os
import re
import shlex
from pathlib import Path

from .. import __author__
from .. import __license__
from .. import __version__
from ..threads.postprocess import PostProcessThread
from ..threads.process import ProcessThread
from ..threads.update_checker import UpdateCheckThread
from ..utils.constants import SOURCE_CODE_LINK
from ..utils.constants import SPLIT_METHOD
from ..utils.constants import SUPPORTS_LOSSY_QUALITY
from ..utils.constants import THEMES
from ..utils.settings import Profile
from ..utils.settings import settings
from .profiles_list_model import ProfilesListModel
from .progressbar_worker import ProgressWorker
from PySide6.QtCore import QFile
from PySide6.QtCore import QIODevice
from PySide6.QtCore import Qt
from PySide6.QtGui import QDesktopServices
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QFileDialog
from PySide6.QtWidgets import QMessageBox
from qt_material import QtStyleTools
from qt_material import apply_stylesheet
from stitchtoon.utils.constants import DETECTION_TYPE
from stitchtoon.utils.constants import SMALLER_ALLOWED_HEIGHT
from stitchtoon.utils.constants import SUPPORTED_IMG_TYPES
from stitchtoon.utils.constants import WIDTH_ENFORCEMENT


QTMATERIAL_PRIMARYTEXTCOLOR = os.environ.get("QTMATERIAL_PRIMARYTEXTCOLOR")
QTMATERIAL_SECONDARYTEXTCOLOR = os.environ.get("QTMATERIAL_SECONDARYTEXTCOLOR")
CUSTOM_CSS = Path(__file__).parent / "resources/custom.css"
LAYOUT = Path(__file__).parent / "resources/layout.ui"
STYLE_EXTRA = {}


class MainWindow(QtStyleTools):
    def __init__(self, parent=None):
        super().__init__()
        self.progress = ProgressWorker()
        self.profilesModel = ProfilesListModel(settings.get_profiles())

        self.ui = self.load_ui()
        self.configure_ui()
        self.connect()

    def load_ui(self) -> None:
        """Loads UI File"""

        loader = QUiLoader()
        ui_file = QFile(LAYOUT)
        ui_file.open(QIODevice.ReadOnly)
        ui = loader.load(ui_file)
        ui_file.close()
        return ui

    def configure_ui(self) -> None:
        """Sets Widgets values against saved settings"""

        # adds items to QComboBox from an iter
        def _set_combo_to_iter(combo, iter, *str_funcs):
            for i in iter:
                name = str(i)
                for func in str_funcs:
                    name = func(name)
                combo.addItem(name)

        # adds items to QComboBox from an enum
        def _set_combo_to_enum(combo, enum, text_value="name", *str_funcs):
            for i in enum:
                if text_value == "name":
                    value = str(i.name)
                elif text_value == "value":
                    value = str(i.value)
                else:
                    return

                for func in str_funcs:
                    value = func(value)

                combo.addItem(value)

        _set_combo_to_enum(
            self.ui.splitMethod,
            SPLIT_METHOD,
            "name",
            str.capitalize,
            lambda s: s.replace("_", " "),
        )
        _set_combo_to_iter(
            self.ui.outputFormat,
            sorted([t for t in SUPPORTED_IMG_TYPES if t.lower() != "jpg"]),
            str.upper,
        )
        _set_combo_to_iter(self.ui.themes, THEMES)
        _set_combo_to_enum(
            self.ui.widthEnforcement, WIDTH_ENFORCEMENT, "value", str.capitalize
        )
        _set_combo_to_enum(
            self.ui.detectionType, DETECTION_TYPE, "value", str.capitalize
        )

        self.ui.profile.setModel(self.profilesModel)
        self.ui.settingsProfiles.setModel(self.profilesModel)

        self.load_profile(settings.get_profile())

        self.show_width_enforcement(self.ui.widthEnforcement.currentText())
        self.show_lossy_quality(self.ui.outputFormat.currentText())

        # --- Post Process ---
        self.enable_postprocess(self.ui.enablePostProcess.isChecked())

        # --- Settings ---
        self.change_theme(settings["theme"])
        self.ui.themes.setCurrentText(settings["theme"])

    def connect(self) -> None:
        """Connects Signals and Slots"""

        # --- Process connections ---

        # links values between progress handler and ui progress bar widget
        self.progress.valueChanged.connect(self.ui.progressBar.setValue)

        # links text between progress handler and ui progress bar widget
        self.progress.textChanged.connect(
            lambda value: self.ui.progressBar.setFormat(f"{value} %p%")
        )

        # --- Settings tab ---

        self.ui.themes.currentTextChanged.connect(self.change_theme)

        # triggers add_profile functionality with profile name
        self.ui.addProfile.clicked.connect(
            lambda: self.add_profile(
                self.ui.profileName.text()
                or self.profilesModel.data(
                    self.ui.settingsProfiles.currentIndex(), Qt.DisplayRole
                )
            )
        )

        # saves widgets values against new profile
        self.profilesModel.profileAdded.connect(
            lambda profile: self.load_profile(profile)
        )

        # saves new profile to settings
        self.profilesModel.profileAdded.connect(
            lambda profile: settings.setValue(
                "profiles", self.profilesModel.getProfiles()
            )
        )

        # saves updated profile to settings
        self.profilesModel.profileUpdated.connect(
            lambda profile: settings.setValue(
                "profiles", self.profilesModel.getProfiles()
            )
        )

        # removes deleted profile from settings
        self.profilesModel.profileDeleted.connect(
            lambda: settings.setValue("profiles", self.profilesModel.getProfiles())
        )

        # removes deleted profile from profilesModel
        self.ui.deleteProfile.clicked.connect(
            lambda: self.profilesModel.deleteProfile(
                self.ui.settingsProfiles.currentIndex()
            )
        )

        # sets ui widgets values against profile changing
        self.ui.settingsProfiles.clicked.connect(
            lambda idx: self.load_profile(
                settings.get_profile(self.profilesModel.data(idx, Qt.DisplayRole))
            )
        )

        self.ui.settingsProfiles.activated.connect(
            lambda idx: self.ui.profile.setCurrentIndex(idx.row())
        )

        self.ui.resetSettings.clicked.connect(self.reset)
        self.ui.sourceLink.clicked.connect(
            lambda: QDesktopServices.openUrl(SOURCE_CODE_LINK)
        )
        self.ui.about.clicked.connect(self.show_about)

        # --- Post process tab ---

        self.ui.postProcessBrowse.clicked.connect(
            lambda: self.ui.postProcessScript.setText(
                self.browse_dialog(self.ui.postProcessScript.text())
            )
        )
        self.ui.enablePostProcess.stateChanged.connect(
            lambda enable: self.enable_postprocess(enable)
        )

        # --- Stitch tab ---

        # changes visibility of lossy quality slider according to chosen format
        self.ui.outputFormat.currentTextChanged.connect(self.show_lossy_quality)

        # changes visibility of width enforcement box according to chosen method
        self.ui.widthEnforcement.currentTextChanged.connect(self.show_width_enforcement)

        # changes visibility advanced options panel

        # updates output field on input field changes
        self.ui.input.textChanged.connect(
            lambda input: self.ui.output.setText(
                self.generate_output_from_input(input)
            )
        )

        # so output field will be updated on profile changes
        self.ui.profile.currentTextChanged.connect(
            lambda x: self.ui.input.textChanged.emit(self.ui.input.text())
        )

        # updates lossy quality label on slider changes
        self.ui.lossyQualitySlider.valueChanged.connect(
            lambda value: self.ui.lossyQuality.setText(f"{value}%")
        )

        # sets ui widgets values against profile changing
        self.ui.profile.currentTextChanged.connect(
            lambda name: self.load_profile(settings.get_profile(name))
        )

        # updates input field when browsing for a path
        self.ui.inputBrowse.clicked.connect(
            lambda: self.ui.input.setText(self.browse_dialog(self.ui.input.text()))
        )

        # updates output field when browsing for a path
        self.ui.outputBrowse.clicked.connect(
            lambda: self.ui.output.setText(self.browse_dialog(self.ui.output.text()))
        )

        # disabled conflicted widgets
        self.ui.matchSource.stateChanged.connect(self.enable_match_source)

        self.ui.start.clicked.connect(self.start)

    def load_profile(self, profile: Profile) -> None:
        """Sets Widgets values according to a profile"""

        self.ui.batchMode.setChecked(profile["batchMode"])
        self.ui.detectionType.setCurrentText(profile["detectionType"])
        self.ui.enablePostProcess.setChecked(profile["enablePostProcess"])
        self.ui.exportArchive.setChecked(profile["exportArchive"])
        self.ui.ignorablePixels.setValue(profile["ignorablePixels"])
        self.ui.lineSteps.setValue(profile["lineSteps"])
        self.ui.lossyQualitySlider.setValue(profile["lossyQuality"])
        self.ui.lossyQuality.setText(f"{self.ui.lossyQualitySlider.value()}%")
        self.ui.outputFormat.setCurrentText(profile["outputFormat"])
        self.ui.profile.setCurrentIndex(
            self.profilesModel.getProfileIndex(profile["name"]).row()
        )
        self.ui.sensitivity.setValue(profile["sensitivity"])
        self.ui.settingsProfiles.setCurrentIndex(
            self.profilesModel.getProfileIndex(profile["name"])
        )
        self.ui.splitValue.setValue(profile["splitValue"])
        self.ui.splitMethod.setCurrentText(profile["splitMethod"].capitalize())
        self.ui.widthEnforcement.setCurrentText(profile["widthEnforcement"])
        self.ui.widthEnforcementSpinBox.setValue(profile["widthEnforcementFixedValue"])
        self.ui.matchSource.setChecked(profile["matchSource"])
        self.ui.writeMetadata.setChecked(profile["writeMetadata"])

        self.enable_match_source(profile["matchSource"])
        if profile["enablePostProcess"]:
            self.ui.postProcessArgs.setText(profile["postProcessArgs"])
            self.ui.postProcessScript.setText(profile["postProcessScript"])

        settings["current-profile"] = profile

    def make_profile(self, name: str) -> dict[str, any]:
        """Creates a profile"""

        profile = {}
        profile["name"] = name
        profile["batchMode"] = self.ui.batchMode.isChecked()
        profile["detectionType"] = self.ui.detectionType.currentText()
        profile["enablePostProcess"] = self.ui.enablePostProcess.isChecked()
        profile["exportArchive"] = self.ui.exportArchive.isChecked()
        profile["ignorablePixels"] = self.ui.ignorablePixels.value()
        profile["lineSteps"] = self.ui.lineSteps.value()
        profile["lossyQuality"] = self.ui.lossyQualitySlider.value()
        profile["outputFormat"] = self.ui.outputFormat.currentText()
        profile["postProcessArgs"] = self.ui.postProcessArgs.text()
        profile["postProcessScript"] = self.ui.postProcessScript.text()
        profile["sensitivity"] = self.ui.sensitivity.value()
        profile["splitValue"] = self.ui.splitValue.value()
        profile["splitMethod"] = self.ui.splitMethod.currentText().lower()
        profile["widthEnforcement"] = self.ui.widthEnforcement.currentText()
        profile["widthEnforcementFixedValue"] = self.ui.widthEnforcementSpinBox.value()
        profile["matchSource"] = self.ui.matchSource.isChecked()
        profile["writeMetadata"] = self.ui.writeMetadata.isChecked()

        return profile

    def add_profile(self, name: str) -> None:
        """makes a profile out of widgets values and saves it in model"""

        profile = self.make_profile(name)
        if self.profilesModel.hasProfile(profile):
            self.profilesModel.updateProfile(profile)
        else:
            self.profilesModel.addProfile(profile)

    def show_lossy_quality(self, format):
        state = False
        if format.lower() in SUPPORTS_LOSSY_QUALITY:
            state = True
        self.ui.lossyQualityWidget.setVisible(state)

    def show_width_enforcement(self, method):
        state = True
        if method.lower() in ("none", "auto", "copywrite"):
            state = False
            self.ui.widthEnforcementSpinBox.setValue(0)
        self.ui.widthEnforcementSpinBox.setVisible(state)

    def change_theme(self, theme):
        settings["theme"] = theme
        theme = theme.lower().replace(" ", "_")
        if "dark" in theme:
            invert_secondary = False
        elif "light" in theme:
            invert_secondary = True

        apply_stylesheet(
            self.ui,
            theme + ".xml",
            invert_secondary=invert_secondary,
            css_file=CUSTOM_CSS,
            extra=STYLE_EXTRA,
        )

    def enable_postprocess(self, state):
        self.ui.postProcessWidget.setEnabled(state)

    def check_for_update(self):
        self.check_update_thread = UpdateCheckThread()
        self.check_update_thread.setTerminationEnabled(True)
        self.check_update_thread.updateAvailable.connect(self.show_update_dialog)

        try:
            self.check_update_thread.start()
        except Exception as e:
            self.status(f"ERROR: {e}", "error")

    def validate_form(self):
        valid = False
        if not self.ui.input.text():
            self.status("Input field can't be empty", "error")
        elif not self.ui.output.text():
            self.status("Input field can't be empty", "error")
        elif not self.ui.splitValue.value():
            self.status("Split value cann't be 0", "error")
        elif (
            self.ui.splitMethod.currentText().upper().replace(" ", "_")
            == "SPLIT_HEIGHT"
            and self.ui.splitValue.value() < SMALLER_ALLOWED_HEIGHT
        ):
            self.status(
                f"Smaller ALLOWED height with `Split height` method is {SMALLER_ALLOWED_HEIGHT}",
                "error",
            )

        elif (
            self.ui.splitMethod.currentText().upper().replace(" ", "_")
            == "IMAGES_NUMBER"
            and self.ui.splitValue.value() > 500
        ):
            self.status(
                "Maximum ALLOWED number with `Images Number` method is 500",
                "error",
            )

        else:
            valid = True

        return valid

    def start(self):
        if not self.validate_form():
            return

        self.progress.update(0)
        self.status("")
        self.ui.postProcessConsole.clear()

        profile = self.make_profile(self.ui.profile.currentText())
        stitch_params = {
            "detection_type": profile["detectionType"].lower(),
            "sensitivity": int(profile["sensitivity"]),
            "custom_width": int(profile["widthEnforcementFixedValue"]),
            "width_enforce": profile["widthEnforcement"],
            "line_steps": int(profile["lineSteps"]),
            "ignorable_pixels": int(profile.get("ignorablePixels")),
        }

        kwargs = {
            "input": self.ui.input.text(),
            "output": self.ui.output.text(),
            "split_height": int(
                profile["splitValue"]
                if self.ui.splitMethod.currentText().upper().replace(" ", "_")
                == "SPLIT_HEIGHT"
                else 0
            ),
            "images_number": int(
                profile["splitValue"]
                if self.ui.splitMethod.currentText().upper().replace(" ", "_")
                == "IMAGES_NUMBER"
                else 0
            ),
            "output_format": profile["outputFormat"],
            "recursive": bool(profile["batchMode"]),
            "as_archive": bool(profile["exportArchive"]),
            "lossy_quality": int(profile["lossyQuality"]),
            "progress": self.progress,
            "slice_to_metadata": bool(profile["matchSource"]),
            "write_metadata": bool(profile["writeMetadata"]),
            "params": stitch_params,
        }

        self.thread = ProcessThread(params=kwargs)
        self.thread.setTerminationEnabled(True)
        self.thread.finished.connect(lambda success: self.ui.start.setEnabled(True))
        self.thread.exceptionRaised.connect(lambda e: self.status(e, "error"))
        self.thread.finished.connect(
            lambda suc: self.postprocess_start() if suc else None
        )
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
        args = (
            " ".join(shlex.split(self.ui.postProcessArgs.text()))
            .replace("$input", self.ui.input.text())
            .replace("$output", self.ui.output.text())
        )
        self.postprocess_thread = PostProcessThread(cmd, args)
        self.postprocess_thread.setTerminationEnabled(True)
        self.postprocess_thread.console.connect(self.postprocess_console)
        self.postprocess_thread.started.connect(
            lambda: self.status("Post Process Started")
        )
        self.postprocess_thread.finished.connect(
            lambda success: self.status("Post Process Finished")
            if success == os.EX_OK
            else self.status("Post Process Faild", "error")
        )
        self.postprocess_thread.finished.connect(
            lambda success: self.ui.start.setEnabled(True)
        )
        self.ui.start.setEnabled(False)

        try:
            self.postprocess_thread.start()
        except Exception as e:
            self.status(f"ERROR: {e}")

    def browse_dialog(self, current_path=None):
        if not current_path:
            start_path = str(Path.home())
        else:
            start_path = current_path

        return (
            QFileDialog.getExistingDirectory(
                self.ui, "Select Directory", start_path, QFileDialog.ShowDirsOnly
            )
            or current_path
        )

    def enable_match_source(self, enable):
        conflicted_widgets = (
            self.ui.widthEnforcement,
            self.ui.widthEnforcementSpinBox,
            self.ui.detectionType,
            self.ui.sensitivity,
            self.ui.lineSteps,
            self.ui.ignorablePixels,
        )
        for widget in conflicted_widgets:
            widget.setEnabled(not enable)

    def show(self):
        self.ui.show()
        self.check_for_update()

    def reset(self):
        settings.reset()
        self.profilesModel.setItems(settings.get_profiles())
        self.load_profile(settings.get_profile())

    def show_update_dialog(self, version, url):
        msg = QMessageBox(self.ui)
        msg.setIcon(QMessageBox.Information)

        msg.setText(f"A New Version is Available {version}")
        msg.setInformativeText(
            f"You are currently using version {__version__}, but version {version} is available. "
            "Do you want to download the latest version?"
        )
        msg.setWindowTitle("Updates")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        retval = msg.exec_()
        if retval == QMessageBox.Yes:
            QDesktopServices.openUrl(url)

    def generate_output_from_input(self, input: str):
        if not input:
            return ""
        repat = "|".join(
            [
                i.replace(" ", ".")
                for i in self.profilesModel.getProfiles().keys()
            ]

        )
        output = str(Path(input).parent / re.sub(repat,"",str(Path(input).name)))
        output += "_" if output[-1] != "_" else ""
        output += self.ui.profile.currentText().replace(" ", "_")
        return output

    def show_about(self):
        msg = QMessageBox(self.ui)
        msg.setText("<h3>Stitchtoon GUI</h3>")
        msg.setInformativeText(
            "<b>The ultimate webtoon stitching tool.</b><br><br>"
            f"Version: {__version__}<br>"
            f"License: {__license__}<br>"
            f"Author: {__author__}<br><br>"
            "This tool is a fork of SmartStitch by MechTechnology."
        )
        msg.setWindowTitle("About")
        msg.setStandardButtons(QMessageBox.Cancel)
        msg.exec_()

    def exit_handler(self):
        settings["current-profile"] = self.make_profile(self.ui.profile.currentText())
        settings.sync()
