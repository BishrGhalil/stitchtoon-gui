from .constants import DEFAULT_PROFILES
from PySide6.QtCore import QSettings
from stitchtoon.utils.constants import ProcessDefaults
from stitchtoon.utils.constants import StitchDefaults


class Settings(QSettings):
    default = {
        "current-profile": list(DEFAULT_PROFILES.keys())[0],
        "profiles": DEFAULT_PROFILES,
        "theme": "dark_teal",
    }

    def __init__(self):
        super().__init__("stitchtoon", "stitchtoon")
        # FIXMEEE
        #  for key in self.default.keys():
        #  if not self.contains(key):
        #  self.reset()
        #  break
        self.reset()

    def reset(self):
        for key, value in self.default.items():
            self.setValue(key, value)

    def get_profile(self, name: str = "current-profile") -> dict[str, any]:
        if name == "current-profile":
            name = self.value("current-profile")
        return self["profiles"].get(name)

    def __setitem__(self, key, value):
        self.setValue(key, value)

    def __getitem__(self, key):
        return self.value(key, None)

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance


settings = Settings()
