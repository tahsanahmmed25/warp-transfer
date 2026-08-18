# Phone-side FOLDER destination picker for Warp Transfer.
#
# Companion to phone_browser_dialog.py's PhoneBrowserDialog (which picks
# FILES/folders to pull FROM the phone) -- this one picks a single
# destination FOLDER to push files/folders TO on the phone, with a
# "New Folder" action, so "Push Files to Phone" is no longer hardcoded to
# /sdcard/Download with no way to choose or create a different destination.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QWidget, QScrollArea, QGraphicsDropShadowEffect,
                             QInputDialog, QLineEdit)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from theme_utils import tag_theme_recursive

DEFAULT_ROOT = "/sdcard"


class PhoneFolderPickerDialog(QDialog):
    """Modal phone-storage folder browser for choosing (or creating) a
    single destination directory. Unlike PhoneBrowserDialog (multi-select,
    files+folders, used for Pull), this is single-target, folders-only
    navigation, with the CURRENT folder being the thing you confirm --
    similar in spirit to a native "Select Folder" dialog, adapted for
    ``adb shell`` since there's no native Android-side folder picker to
    call into from a desktop app."""

    def __init__(self, adb_manager, is_dark: bool, start_path: str, parent=None):
        super().__init__(parent)
        self.adb_manager = adb_manager
        self.setWindowTitle("Choose Destination Folder")
        self.setModal(True)
        self.setFixedSize(460, 540)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.current_path = start_path or DEFAULT_ROOT
        self.chosen_path = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        self.card = QWidget(self)
        self.card.setObjectName("CardContainer")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(22, 20, 22, 20)
        card_layout.setSpacing(10)

        title = QLabel("Choose Destination Folder", self.card)
        title.setObjectName("HeaderLabel")
        title.setStyleSheet("font-size: 17px;")
        card_layout.addWidget(title)

        subtitle = QLabel("Files will be pushed into the folder you're currently viewing.", self.card)
        subtitle.setObjectName("SubHeaderLabel")
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)

        nav_row = QHBoxLayout()
        self.up_btn = QPushButton("\u2191 Up", self.card)
        self.up_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.up_btn.clicked.connect(self._go_up)
        nav_row.addWidget(self.up_btn)
        self.path_label = QLabel(self.current_path, self.card)
        self.path_label.setObjectName("PathLabel")
        self.path_label.setWordWrap(True)
        nav_row.addWidget(self.path_label, 1)
        card_layout.addLayout(nav_row)

        self.status_label = QLabel("", self.card)
        self.status_label.setObjectName("StatusBannerWarning")
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        card_layout.addWidget(self.status_label)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.list_widget = QWidget()
        self.list_layout = QVBoxLayout(self.list_widget)
        self.list_layout.setSpacing(4)
        self.list_layout.setContentsMargins(0, 4, 0, 4)
        self.scroll.setWidget(self.list_widget)
        card_layout.addWidget(self.scroll, 1)

        new_folder_btn = QPushButton("+ New Folder Here", self.card)
        new_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        new_folder_btn.clicked.connect(self._create_folder)
        card_layout.addWidget(new_folder_btn)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel", self.card)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        self.confirm_btn = QPushButton("Push Here", self.card)
        self.confirm_btn.setObjectName("PrimaryButton")
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.clicked.connect(self._confirm_current)
        btn_row.addWidget(self.confirm_btn)
        card_layout.addLayout(btn_row)

        outer.addWidget(self.card)
        shadow = QGraphicsDropShadowEffect(self.card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.card.setGraphicsEffect(shadow)

        tag_theme_recursive(self, is_dark)
        self._load_dir(self.current_path)

    def _list_dirs(self, path: str):
        """Returns a sorted list of subdirectory names under `path`, or
        None on an adb error. Folders-only (unlike PhoneBrowserDialog's
        _list_dir) since a destination target has to be a directory."""
        code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"ls -1p '{path}'"])
        if code != 0:
            return None
        dirs = []
        for line in (stdout or "").splitlines():
            name = line.strip()
            if name.endswith("/"):
                dirs.append(name[:-1])
        return sorted(dirs)

    def _load_dir(self, path: str):
        self.current_path = path
        self.path_label.setText(path)
        self.up_btn.setEnabled(path not in ("/sdcard", "/"))

        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        dirs = self._list_dirs(path)
        if dirs is None:
            self.status_label.setText(
                "Couldn't read this folder \u2014 it may need different permissions, or doesn't exist."
            )
            self.status_label.setVisible(True)
            return
        self.status_label.setVisible(False)

        if not dirs:
            empty = QLabel("No subfolders here. Use \u201c+ New Folder Here\u201d to create one, "
                            "or tap \u201cPush Here\u201d to use this folder.", self.list_widget)
            empty.setObjectName("SubHeaderLabel")
            empty.setWordWrap(True)
            self.list_layout.addWidget(empty)
            return

        for name in dirs:
            full_path = f"{path.rstrip('/')}/{name}"
            self.list_layout.addWidget(self._build_row(name, full_path))

    def _build_row(self, name: str, full_path: str) -> QWidget:
        row = QPushButton(f"\U0001F4C1  {name}")
        row.setObjectName("LinkButton")
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.clicked.connect(lambda: self._load_dir(full_path))
        return row

    def _go_up(self):
        if self.current_path in ("/sdcard", "/"):
            return
        parent = self.current_path.rsplit("/", 1)[0] or "/"
        self._load_dir(parent)

    def _create_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:", QLineEdit.EchoMode.Normal, "")
        name = (name or "").strip()
        if not ok or not name:
            return
        # Reject path separators outright rather than letting a stray "/"
        # silently create nested folders the user didn't ask for, or ".."
        # escape the current directory.
        if "/" in name or name in (".", ".."):
            self.status_label.setText("Folder name can't contain \u201c/\u201d.")
            self.status_label.setVisible(True)
            return
        new_path = f"{self.current_path.rstrip('/')}/{name}"
        code, _, stderr = self.adb_manager.run_adb_cmd(["shell", "mkdir", "-p", f"'{new_path}'"])
        if code != 0:
            self.status_label.setText(f"Couldn't create folder: {stderr.strip() if stderr else 'unknown error'}")
            self.status_label.setVisible(True)
            return
        self._load_dir(new_path)  # navigate straight into the folder just created

    def _confirm_current(self):
        self.chosen_path = self.current_path
        self.accept()

    @staticmethod
    def ask(adb_manager, is_dark: bool, start_path: str = DEFAULT_ROOT, parent=None):
        """Returns the chosen absolute phone folder path, or None if the
        user cancelled."""
        dlg = PhoneFolderPickerDialog(adb_manager, is_dark, start_path, parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.chosen_path
        return None
