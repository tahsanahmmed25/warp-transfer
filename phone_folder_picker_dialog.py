# Phone-side FOLDER destination picker for Warp Transfer.
#
# Lets the user navigate the connected device's storage and select or create
# a destination folder for transfers.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QWidget, QScrollArea, QGraphicsDropShadowEffect,
                             QInputDialog, QLineEdit, QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

from theme_utils import tag_theme_recursive

DEFAULT_ROOT = "/sdcard"

_SVG_FOLDER = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>'


def _folder_icon_badge(is_dark: bool) -> QWidget:
    badge = QWidget()
    badge.setObjectName("IconBadge")
    badge.setFixedSize(32, 32)
    layout = QVBoxLayout(badge)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    color = "#D4AF37" if is_dark else "#B8860B"
    pixmap = QPixmap(QSize(16, 16))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(_SVG_FOLDER.format(color=color).encode("utf-8")).render(painter)
    painter.end()
    
    label = QLabel()
    label.setPixmap(pixmap)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    return badge


class PhoneFolderPickerDialog(QDialog):
    """Modal phone-storage folder browser for choosing (or creating) a
    single destination directory."""

    def __init__(self, adb_manager, is_dark: bool, start_path: str = DEFAULT_ROOT, parent=None):
        super().__init__(parent)
        self.adb_manager = adb_manager
        self.is_dark = is_dark
        self.setWindowTitle("Choose Destination Folder")
        self.setModal(True)
        self.setFixedSize(560, 620)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.current_path = start_path or DEFAULT_ROOT
        self.chosen_path = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        self.card = QWidget(self)
        self.card.setObjectName("CardContainer")
        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(24, 22, 24, 22)
        card_layout.setSpacing(12)

        title = QLabel("Choose Destination Folder", self.card)
        title.setObjectName("HeaderLabel")
        title.setStyleSheet("font-size: 18px;")
        card_layout.addWidget(title)

        subtitle = QLabel("Files will be saved into the folder you're currently viewing.", self.card)
        subtitle.setObjectName("SubHeaderLabel")
        subtitle.setWordWrap(True)
        card_layout.addWidget(subtitle)

        # Interactive breadcrumb bar
        self.breadcrumb_wrap = QWidget(self.card)
        self.breadcrumb_wrap.setObjectName("BreadcrumbWrap")
        self.breadcrumb_row = QHBoxLayout(self.breadcrumb_wrap)
        self.breadcrumb_row.setContentsMargins(8, 4, 8, 4)
        self.breadcrumb_row.setSpacing(4)
        card_layout.addWidget(self.breadcrumb_wrap)

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
        self.confirm_btn = QPushButton("Save Here", self.card)
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

        tag_theme_recursive(self, self.is_dark)
        self._load_dir(self.current_path)

    def _list_dirs(self, path: str):
        """Returns a sorted list of subdirectory names under `path`."""
        code, stdout, _ = self.adb_manager.run_adb_cmd(["shell", f"ls -1p '{path}'"])
        if code != 0:
            return None
        dirs = []
        for line in (stdout or "").splitlines():
            name = line.strip()
            if name.endswith("/"):
                dirs.append(name[:-1])
        return sorted(dirs)

    def _rebuild_breadcrumb(self, path: str):
        while self.breadcrumb_row.count():
            item = self.breadcrumb_row.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        segments = [s for s in path.strip("/").split("/") if s]
        accumulated = ""
        for i, seg in enumerate(segments):
            accumulated += f"/{seg}"
            crumb = QPushButton(seg, self.breadcrumb_wrap)
            crumb.setObjectName("BreadcrumbBtn")
            crumb.setCursor(Qt.CursorShape.PointingHandCursor)
            crumb.clicked.connect(lambda checked=False, p=accumulated: self._load_dir(p))
            self.breadcrumb_row.addWidget(crumb)
            if i < len(segments) - 1:
                sep = QLabel("/", self.breadcrumb_wrap)
                sep.setObjectName("BreadcrumbSep")
                self.breadcrumb_row.addWidget(sep)
        self.breadcrumb_row.addStretch()
        tag_theme_recursive(self.breadcrumb_wrap, self.is_dark)

    def _load_dir(self, path: str):
        self.current_path = path
        self._rebuild_breadcrumb(path)

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
                            "or tap \u201cSave Here\u201d to use this folder.", self.list_widget)
            empty.setObjectName("SubHeaderLabel")
            empty.setWordWrap(True)
            self.list_layout.addWidget(empty)
            tag_theme_recursive(empty, self.is_dark)
            return

        for name in dirs:
            full_path = f"{path.rstrip('/')}/{name}"
            row = self._build_row(name, full_path)
            self.list_layout.addWidget(row)
            tag_theme_recursive(row, self.is_dark)

    def _build_row(self, name: str, full_path: str) -> QWidget:
        row = QWidget()
        row.setObjectName("InnerCard")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 6, 12, 6)
        row_layout.setSpacing(10)

        row_layout.addWidget(_folder_icon_badge(self.is_dark))

        label = QPushButton(name, row)
        label.setObjectName("BrowserDirBtn")
        label.setCursor(Qt.CursorShape.PointingHandCursor)
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        label.clicked.connect(lambda: self._load_dir(full_path))
        row_layout.addWidget(label, 1)

        chevron = QLabel("\u203a", row)
        chevron.setObjectName("BrowserChevron")
        row_layout.addWidget(chevron)

        return row

    def _create_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:", QLineEdit.EchoMode.Normal, "")
        name = (name or "").strip()
        if not ok or not name:
            return
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
        self._load_dir(new_path)

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
