# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.

from enum import Enum


DEFAULT_THEME = "dark_teal"
SUPPORTS_LOSSY_QUALITY = ("jpeg", "webp")
THEMES = (
    "Dark Cyan",
    "Dark Pink",
    "Dark Teal",
    "Dark Yellow",
    "Light Amber",
    "Light Cyan",
    "Light Pink",
    "Light Teal",
)
LOG_REL_DIR = "__logs__"
SOURCE_CODE_LINK = "https://github.com/BishrGhalil/stitchtoon-gui"


class SPLIT_METHOD(Enum):
    SPLIT_HEIGHT = 0
    IMAGES_NUMBER = 1


DEFAULT_PROFILES = {
    "To Edit": {
        "name": "To Edit",
        "outputFormat": "PSD",
        "widthEnforcement": "Auto",
        "detectionType": "pixel",
        "lossyQuality": 90,
        "widthEnforcementFixedValue": -1,
        "splitValue": 50_000,
        "splitMethod": "split height",
        "sensitivity": 80,
        "lineSteps": 30,
        "ignorablePixels": 20,
        "batchMode": False,
        "exportArchive": False,
        "enablePostProcess": False,
    },
    "Ready": {
        "name": "Ready",
        "outputFormat": "JPEG",
        "widthEnforcement": "Fixed",
        "detectionType": "pixel",
        "lossyQuality": 86,
        "widthEnforcementFixedValue": 760,
        "splitValue": 4608,
        "splitMethod": "split height",
        "sensitivity": 100,
        "lineSteps": 5,
        "ignorablePixels": 20,
        "batchMode": False,
        "exportArchive": True,
        "enablePostProcess": False,
    },
    "Manga To Edit": {
        "name": "Manga To Edit",
        "outputFormat": "PSD",
        "widthEnforcement": "None",
        "detectionType": "pixel",
        "lossyQuality": 90,
        "widthEnforcementFixedValue": -1,
        "splitValue": 50_000,
        "splitMethod": "split height",
        "sensitivity": 80,
        "lineSteps": 30,
        "ignorablePixels": 20,
        "batchMode": False,
        "exportArchive": False,
        "enablePostProcess": False,
    },
    "Manga Ready": {
        "name": "Manga Ready",
        "outputFormat": "JPEG",
        "widthEnforcement": "copywrite",
        "detectionType": "pixel",
        "lossyQuality": 86,
        "widthEnforcementFixedValue": -1,
        "splitValue": 0,
        "splitMethod": "images number",
        "sensitivity": 100,
        "lineSteps": 5,
        "ignorablePixels": 20,
        "batchMode": False,
        "exportArchive": True,
        "enablePostProcess": False,
    },
}
