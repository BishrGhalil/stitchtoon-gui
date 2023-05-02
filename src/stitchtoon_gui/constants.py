DEFAULT_THEME = "dark_teal"
SUPPORTS_LOSSY_QUALITY = ("jpeg", "webp")
LOG_REL_DIR = "__logs__"
OUTPUT_SUFFIX = " [stitched]"

DEFAULT_PROFILES = {
    "pre-edit": {
        "name": "pre-edit",
        "outputFormat": "PSD",
        "widthEnforcement": "Auto",
        "detectionType": "pixel",
        "lossyQuality": 90,
        "widthEnforcementFixedValue": -1,
        "splitHeight": 40_000,
        "sensitivity": 90,
        "lineSteps": 5,
        "ignorablePixels": 20,
        "batchMode": False,
        "exportArchive": False,
    },
    "post-edit": {
        "name": "post-edit",
        "outputFormat": "JPEG",
        "widthEnforcement": "None",
        "detectionType": "pixel",
        "lossyQuality": 88,
        "widthEnforcementFixedValue": -1,
        "splitHeight": 5000,
        "sensitivity": 100,
        "lineSteps": 5,
        "ignorablePixels": 20,
        "batchMode": False,
        "exportArchive": True,
    },
}
