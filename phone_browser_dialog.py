# Phone-side file/folder browser dialog for Warp Transfer.
#
# Lets the user navigate the connected device's storage and check specific
# files/folders to pull to the PC. Previously "Pull Custom Files" silently
# always grabbed a hardcoded /sdcard/Download regardless of what the
# button's own label implied -- this is the actual picker that label was
# always supposed to open, per Tahsan's real-device testing feedback.
#
# Redesigned (per direct request, alongside the "from and to" destination-
# picking work in phone_folder_picker_dialog.py): larger dialog, distinct
# folder-vs-file row styling (rounded icon badges instead of raw emoji-in-
# QLabel text, folders visually distinct from files with a chevron hint),
# and a breadcrumb-style path row instead of one long unbroken path string.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QWidget, QScrollArea, QGraphicsDropShadowEffect, QCheckBox,
                             QSizePolicy)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from theme_utils import tag_theme_recursive

DEFAULT_ROOT = "/sdcard"


def _row_icon_badge(is_dir: bool) -> QWidget:
    """Small rounded icon badge distinguishing folders from files, replacing
    the previous raw emoji-glued-into-label-text approach -- consistent
    with the IconBadge look used everywhere else in the app instead of
    looking like a one-off in this dialog specifically."""
    badge = QWidget()
    badge.setObjectName("IconBadge")
    badge.setFixedSize(30, 30)
    layout = QVBoxLayout(badge)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label = QLabel("\U0001F4C1" if is_dir else "\U0001F4C4")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setStyleSheet("font-size: 14px; background: transparent; border: none;")
    layout.addWidget(label)
    return badge


class PhoneBrowserDialog(QDialog):
    """Modal phone-storage browser: navigate folders, check items across
    any number of folders visited, confirm a selection of absolute paths.
    Selections persist as you navigate in and out of folders (tracked on
    the dialog instance, not per-listing), so picking a file in one folder
    then browsing into a different one doesn't lose the earlier pick."""

    def __init__(self, adb_manager, is_dark: bool, parent=None):
        super().__init__(parent)
        self.adb_manager = adb_manager
        self.setWindowTitle("Choose Files to Pull")
        self.setModal(True)
        self.setFixedSize(540, 620)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.current_path = DEFAULT_ROOT
        self.selected_paths = set()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        self.card = QWidget(self)
        self.card.setObjectName("CardContainer")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(12)

        header_row = QHBoxLayout()
        title = QLabel("Choose Files to Pull", self.card)
        title.setObjectName("HeaderLabel")
        title.setStyleSheet("font-size: 18px;")
        header_row.addWidget(title)
        header_row.addStretch()
        self.selection_summary = QLabel("No items selected yet.", self.card)
        self.selection_summary.setObjectName("SubHeaderLabel")
        header_row.addWidget(self.selection_summary)
        card_layout.addLayout(header_row)

        # Breadcrumb-style path row: each ancestor segment is its own
        # clickable link, so jumping back up several levels at once doesn't
        # require repeated "Up" clicks -- previously the whole path was one
        # long, non-interactive wrapped string.
        self.breadcrumb_row = QHBoxLayout()
        self.breadcrumb_row.setSpacing(2)
        breadcrumb_wrap = QWidget(self.card)
        breadcrumb_wrap.setLayout(self.breadcrumb_row)
        breadcrumb_wrap.setObjectName("InnerCard")
        card_layout.addWidget(breadcrumb_wrap)

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
        self.list_layout.setSpacing(6)
        self.list_layout.setContentsMargins(0, 6, 0, 6)
        self.scroll.setWidget(self.list_widget)
        card_layout.addWidget(self.scroll, 1)

        btn_row = QHBoxLayout()
        cancel_btn = QPushButton("Cancel", self.card)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)
        self.confirm_btn = QPushButton("Use Selected Items", self.card)
        self.confirm_btn.setObjectName("PrimaryButton")
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.clicked.connect(self.accept)
        self.confirm_btn.setEnabled(False)
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

    def _list_dir(self, path: str):
        """Returns (dirs, files) sorted name lists for `path`, or
        (None, None) on an adb error. Deliberately uses `ls -1p` (one entry
        per line, trailing '/' on directories) rather than `ls -la` --
        Android's toybox `ls -la` column layout and date format aren't
        reliably parseable across OEM skins/OS versions, and a picker only
        actually needs name + dir-or-file, which `-1p` gives directly in a
        far simpler, more robust format."""
        code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"ls -1p '{path}'"])
        if code != 0:
            return None, None
        dirs, files = [], []
        for line in (stdout or "").splitlines():
            name = line.strip()
            if not name:
                continue
            if name.endswith("/"):
                dirs.append(name[:-1])
            else:
                files.append(name)
        return sorted(dirs), sorted(files)

    def _rebuild_breadcrumb(self, path: str):
        while self.breadcrumb_row.count():
            item = self.breadcrumb_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        segments = [s for s in path.strip("/").split("/") if s]
        accumulated = ""
        for i, seg in enumerate(segments):
            accumulated += f"/{seg}"
            crumb = QPushButton(seg, self.card)
            crumb.setObjectName("GhostTextLink")
            crumb.setCursor(Qt.CursorShape.PointingHandCursor)
            crumb.clicked.connect(lambda checked=False, p=accumulated: self._load_dir(p))
            self.breadcrumb_row.addWidget(crumb)
            if i < len(segments) - 1:
                sep = QLabel("/", self.card)
                sep.setObjectName("SubHeaderLabel")
                self.breadcrumb_row.addWidget(sep)
        self.breadcrumb_row.addStretch()

    def _load_dir(self, path: str):
        self.current_path = path
        self._rebuild_breadcrumb(path)

        while self.list_layout.count():
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        dirs, files = self._list_dir(path)
        if dirs is None:
            self.status_label.setText(
                "Couldn't read this folder \u2014 it may need different permissions, or doesn't exist."
            )
            self.status_label.setVisible(True)
            return
        self.status_label.setVisible(False)

        if not dirs and not files:
            empty = QLabel("This folder is empty.", self.list_widget)
            empty.setObjectName("SubHeaderLabel")
            self.list_layout.addWidget(empty)
            return

        for name in dirs:
            full_path = f"{path.rstrip('/')}/{name}"
            self.list_layout.addWidget(self._build_row(name, full_path, is_dir=True))
        for name in files:
            full_path = f"{path.rstrip('/')}/{name}"
            self.list_layout.addWidget(self._build_row(name, full_path, is_dir=False))

    def _build_row(self, name: str, full_path: str, is_dir: bool) -> QWidget:
        row = QWidget()
        row.setObjectName("InnerCard")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 6, 10, 6)
        row_layout.setSpacing(10)

        checkbox = QCheckBox(row)
        checkbox.setChecked(full_path in self.selected_paths)
        checkbox.stateChanged.connect(lambda state, p=full_path: self._toggle_selection(p, state))
        row_layout.addWidget(checkbox)

        row_layout.addWidget(_row_icon_badge(is_dir))

        if is_dir:
            label = QPushButton(name, row)
            label.setObjectName("LinkButton")
            label.setCursor(Qt.CursorShape.PointingHandCursor)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            label.clicked.connect(lambda: self._load_dir(full_path))
        else:
            label = QLabel(name, row)
            label.setObjectName("TransferDetailLabel")
        row_layout.addWidget(label, 1)

        if is_dir:
            chevron = QLabel("\u203a", row)
            chevron.setObjectName("SubHeaderLabel")
            row_layout.addWidget(chevron)

        return row

    def _toggle_selection(self, full_path: str, state):
        if state:
            self.selected_paths.add(full_path)
        else:
            self.selected_paths.discard(full_path)
        count = len(self.selected_paths)
        self.selection_summary.setText(f"{count} item(s) selected." if count else "No items selected yet.")
        self.confirm_btn.setEnabled(count > 0)

    @staticmethod
    def ask(adb_manager, is_dark: bool, parent=None) -> list:
        """Returns a list of absolute phone paths the user selected, or an
        empty list if they cancelled or confirmed with nothing checked."""
        dlg = PhoneBrowserDialog(adb_manager, is_dark, parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return list(dlg.selected_paths)
        return []
