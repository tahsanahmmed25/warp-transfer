# Phone-side file/folder browser dialog for Warp Transfer.
#
# Lets the user navigate the connected device's storage and check specific
# files/folders to pull to the PC.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QWidget, QScrollArea, QGraphicsDropShadowEffect, QCheckBox,
                             QSizePolicy)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

from theme_utils import tag_theme_recursive

DEFAULT_ROOT = "/sdcard"

_SVG_FOLDER = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>'
_SVG_FILE = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>'


def _row_icon_badge(is_dir: bool, is_dark: bool) -> QWidget:
    """Rounded vector icon badge distinguishing folders from files."""
    badge = QWidget()
    badge.setObjectName("IconBadge")
    badge.setFixedSize(32, 32)
    layout = QVBoxLayout(badge)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    color = "#D4AF37" if is_dark else "#B8860B"
    svg_str = _SVG_FOLDER.format(color=color) if is_dir else _SVG_FILE.format(color=color)
    
    pixmap = QPixmap(QSize(16, 16))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(svg_str.encode("utf-8")).render(painter)
    painter.end()
    
    label = QLabel()
    label.setPixmap(pixmap)
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(label)
    return badge


class PhoneBrowserDialog(QDialog):
    """Modal phone-storage browser: navigate folders, check items across
    any number of folders visited, confirm a selection of absolute paths."""

    def __init__(self, adb_manager, is_dark: bool, parent=None):
        super().__init__(parent)
        self.adb_manager = adb_manager
        self.is_dark = is_dark
        self.setWindowTitle("Choose Files to Pull")
        self.setModal(True)
        self.setFixedSize(560, 640)
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

        tag_theme_recursive(self, self.is_dark)
        self._load_dir(self.current_path)

    def _list_dir(self, path: str):
        """Returns (dirs, files) sorted name lists for `path`."""
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
            tag_theme_recursive(empty, self.is_dark)
            return

        for name in dirs:
            full_path = f"{path.rstrip('/')}/{name}"
            row = self._build_row(name, full_path, is_dir=True)
            self.list_layout.addWidget(row)
            tag_theme_recursive(row, self.is_dark)
        for name in files:
            full_path = f"{path.rstrip('/')}/{name}"
            row = self._build_row(name, full_path, is_dir=False)
            self.list_layout.addWidget(row)
            tag_theme_recursive(row, self.is_dark)

    def _build_row(self, name: str, full_path: str, is_dir: bool) -> QWidget:
        row = QWidget()
        row.setObjectName("InnerCard")
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(10, 6, 12, 6)
        row_layout.setSpacing(10)

        checkbox = QCheckBox(row)
        checkbox.setChecked(full_path in self.selected_paths)
        checkbox.stateChanged.connect(lambda state, p=full_path: self._toggle_selection(p, state))
        row_layout.addWidget(checkbox)

        row_layout.addWidget(_row_icon_badge(is_dir, self.is_dark))

        if is_dir:
            label = QPushButton(name, row)
            label.setObjectName("BrowserDirBtn")
            label.setCursor(Qt.CursorShape.PointingHandCursor)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            label.clicked.connect(lambda: self._load_dir(full_path))
        else:
            label = QLabel(name, row)
            label.setObjectName("BrowserFileLabel")
        row_layout.addWidget(label, 1)

        if is_dir:
            chevron = QLabel("\u203a", row)
            chevron.setObjectName("BrowserChevron")
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
