# This file is part of stitchtoon.
# License: MIT, see the file "LICENSE" for details.

from ..utils.settings import Profile
from PySide6.QtCore import QAbstractListModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import Qt
from PySide6.QtCore import Signal


class ProfilesListModel(QAbstractListModel):
    profileAdded = Signal(dict)
    profileUpdated = Signal(dict)
    profileDeleted = Signal()

    def __init__(self, profiles: dict[str, Profile] = None, parent=None):
        super().__init__(parent)
        self.profiles = profiles

    def rowCount(self, parent=QModelIndex()):
        return len(self.profiles.keys())

    def data(self, index, role):
        row = index.row()
        if not index.isValid() or row >= len(self.profiles.keys()):
            return None
        if role == Qt.DisplayRole:
            return list(self.profiles.keys())[row]
        elif role == Qt.ItemDataRole:
            return list(self.profiles.values())[row]
        else:
            return None

    def getProfileIndex(self, name: str):
        return self.createIndex(list(self.profiles.keys()).index(name), 0, 0)

    def setItems(self, profiles: dict[str, Profile]):
        self.beginResetModel()
        self.profiles = profiles
        self.endResetModel()

    def addProfile(self, profile: Profile):
        self.beginInsertRows(QModelIndex(), self.rowCount() - 1, 1)
        self.profiles[profile["name"]] = profile
        self.endInsertRows()
        self.profileAdded.emit(profile)

    def updateProfile(self, profile: Profile):
        self.profiles[profile["name"]] = profile
        self.profileUpdated.emit(profile)

    def deleteProfile(self, index):
        name = list(self.profiles.keys())[index.row()]
        self.beginRemoveRows(QModelIndex(), index.row(), index.row())
        del self.profiles[name]
        self.endRemoveRows()
        self.profileDeleted.emit()

    def getProfiles(self):
        return self.profiles

    def hasProfile(self, profile: Profile):
        return self.profiles.get(profile["name"]) is not None
