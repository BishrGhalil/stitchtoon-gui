# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.

from .constants import DEFAULT_PROFILES
from PySide6.QtCore import QSettings


Profile = dict[str, any]


class Settings(QSettings):
    default = {
        "current-profile": DEFAULT_PROFILES.get(list(DEFAULT_PROFILES.keys())[0]),
        "profiles": DEFAULT_PROFILES,
        "theme": "dark_teal",
        "used-before": False,
    }

    def __init__(self):
        super().__init__("stitchtoon", "stitchtoon")
        if not self["used-before"] or not self["profiles"]:
            self.reset()
            self["used-before"] = True

    def reset(self):
        for key, value in self.default.items():
            self.setValue(key, value)
        self.sync()

    def get_profiles(self) -> dict[str, Profile]:
        return self.get("profiles", self.default["profiles"])

    def get_profile(self, name: str = "") -> Profile:
        if isinstance(name, dict):
            name = name["name"]
        if not name or not self.get_profiles().get(name):
            return self.value("current-profile")
        return self.get_profiles().get(name)

    def get(self, key, *args, **kwargs):
        return self.value(key, *args, **kwargs)

    def __setitem__(self, key, value):
        self.setValue(key, value)

    def __getitem__(self, key):
        return self.value(key)

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Settings, cls).__new__(cls)
        return cls.instance


settings = Settings()
