# Warp Transfer Main Application (PyQt6 Modern GUI Wrapper)

import os
import sys
import json
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QStackedWidget, 
                             QProgressBar, QFileDialog, QGraphicsDropShadowEffect,
                             QGraphicsOpacityEffect, QScrollArea)
from PyQt6.QtCore import Qt, QSize, QTimer, QPoint, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QColor, QIcon, QPixmap, QPainter, QDragEnterEvent, QDropEvent
from PyQt6.QtSvg import QSvgRenderer

from app_style import APP_STYLE
from adb_manager import AdbManager
from onboarding_wizard import OnboardingWizard
from transfer_engine import TransferCoordinator
import history_manager
from conflict_dialog import ConflictDialog
from device_picker import DevicePickerDialog
from wireless_connect_dialog import WirelessConnectDialog
from phone_browser_dialog import PhoneBrowserDialog
from phone_folder_picker_dialog import PhoneFolderPickerDialog

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

from ui_transitions import fade_to_page
from theme_utils import tag_theme_recursive

# Raw SVG Icons (Lucide style)
SVG_PHONE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/></svg>'
SVG_PC = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="20" height="14" x="2" y="3" rx="2"/><line x1="8" x2="16" y1="21" y2="21"/><line x1="12" x2="12" y1="17" y2="21"/></svg>'
SVG_FOLDER = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>'
SVG_FILE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/></svg>'
SVG_PLUS = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" x2="12" y1="5" y2="19"/><line x1="5" x2="19" y1="12" y2="12"/></svg>'
SVG_ARROW_LEFT_RIGHT = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 3 4 4-4 4"/><path d="M20 7H4"/><path d="m8 21-4-4 4-4"/><path d="M4 17h16"/></svg>'
SVG_SWAP = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M7 16V4M7 4 3 8M7 4l4 4M17 8v12M17 20l-4-4M17 20l4-4"/></svg>'
SVG_CHECK = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#34C759" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>'
SVG_ALERT = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#FF453A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>'
SVG_DOWNLOAD = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>'
SVG_CLOSE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>'
SVG_MINIMIZE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" x2="19" y1="12" y2="12"/></svg>'
SVG_ZAP = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
SVG_SEARCH = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" x2="16.65" y1="21" y2="16.65"/></svg>'
SVG_SHIELD = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>'
SVG_HELP_CIRCLE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>'
SVG_LINK = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>'
SVG_MOON = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#8E8E93" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'
SVG_SUN = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="M4.93 4.93l1.41 1.41"/><path d="M17.66 17.66l1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="M6.34 17.66l-1.41 1.41"/><path d="M19.07 4.93l-1.41 1.41"/></svg>'
SVG_HISTORY = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l4 2"/></svg>'
SVG_SETTINGS = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>'
SVG_WIFI = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 13a10 10 0 0 1 14 0"/><path d="M8.5 16.5a5 5 0 0 1 7 0"/><path d="M2 8.82a15 15 0 0 1 20 0"/><line x1="12" x2="12.01" y1="20" y2="20"/></svg>'
SVG_PAUSE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="{color}" stroke="none"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>'
SVG_PLAY = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="{color}" stroke="none"><polygon points="6 3 20 12 6 21 6 3"/></svg>'
SVG_BACK = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 19-7-7 7-7"/><path d="M19 12H5"/></svg>'
SVG_IMAGE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/></svg>'
SVG_VIDEO = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m22 8-6 4 6 4V8Z"/><rect width="14" height="12" x="2" y="6" rx="2" ry="2"/></svg>'
SVG_TRASH = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>'
SVG_COPY = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="14" x="8" y="8" rx="2" ry="2"/><path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/></svg>'
SVG_MOVE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="5 9 2 12 5 15"/><polyline points="9 5 12 2 15 5"/><polyline points="15 19 12 22 9 19"/><polyline points="19 9 22 12 19 15"/><line x1="2" x2="22" y1="12" y2="12"/><line x1="12" x2="12" y1="2" y2="22"/></svg>'

PHOTO_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "heic", "gif", "bmp"]
VIDEO_EXTENSIONS = ["mp4", "mov", "mkv", "3gp", "avi", "webm"]


def get_svg_content(icon_name, is_dark) -> str:
    accent = "#D4AF37" if is_dark else "#B8860B"
    text_color = "#F2F2F7" if is_dark else "#1C1C1E"
    muted = "#9C9CA3" if is_dark else "#8E8E93"
    
    if icon_name == "phone":
        return SVG_PHONE.format(color=accent)
    elif icon_name == "pc":
        return SVG_PC.format(color=accent)
    elif icon_name == "folder":
        return SVG_FOLDER.format(color=accent)
    elif icon_name == "file":
        return SVG_FILE.format(color=accent)
    elif icon_name == "plus":
        return SVG_PLUS.format(color=accent)
    elif icon_name == "arrow_left_right":
        return SVG_ARROW_LEFT_RIGHT.format(color=text_color)
    elif icon_name == "swap":
        return SVG_SWAP.format(color=accent)
    elif icon_name == "close":
        return SVG_CLOSE.format(color=muted)
    elif icon_name == "minimize":
        return SVG_MINIMIZE.format(color=muted)
    elif icon_name == "moon":
        return SVG_MOON
    elif icon_name == "sun":
        return SVG_SUN.format(color=accent)
    elif icon_name == "download":
        return SVG_DOWNLOAD.format(color=accent)
    elif icon_name == "check":
        return SVG_CHECK
    elif icon_name == "alert":
        return SVG_ALERT
    elif icon_name == "zap":
        return SVG_ZAP.format(color=accent)
    elif icon_name == "search":
        return SVG_SEARCH.format(color=accent)
    elif icon_name == "shield":
        return SVG_SHIELD.format(color=accent)
    elif icon_name == "help_circle":
        return SVG_HELP_CIRCLE.format(color=accent)
    elif icon_name == "link":
        return SVG_LINK.format(color=accent)
    elif icon_name == "history":
        return SVG_HISTORY.format(color=muted)
    elif icon_name == "settings":
        return SVG_SETTINGS.format(color=muted)
    elif icon_name == "wifi":
        return SVG_WIFI.format(color=accent)
    elif icon_name == "pause":
        return SVG_PAUSE.format(color=text_color)
    elif icon_name == "play":
        return SVG_PLAY.format(color="#14140E" if is_dark else "#FFFFFF")
    elif icon_name == "back":
        return SVG_BACK.format(color=muted)
    elif icon_name == "image":
        return SVG_IMAGE.format(color=accent)
    elif icon_name == "video":
        return SVG_VIDEO.format(color=accent)
    elif icon_name == "trash":
        return SVG_TRASH.format(color="#FF6961")
    elif icon_name == "copy":
        return SVG_COPY.format(color=accent)
    elif icon_name == "move":
        return SVG_MOVE.format(color=accent)
    return ""


def add_shadow(widget, blur=24, y_offset=6, alpha=90):
    """Attach a soft drop shadow to a widget for subtle elevation."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)
    return shadow


def make_icon_badge(icon_name, is_dark, size=40, icon_size=20):
    """Return a small rounded badge QWidget with a centered icon, used for
    quick-action buttons and card headers."""
    badge = QWidget()
    badge.setObjectName("IconBadge")
    badge.setFixedSize(size, size)
    b_layout = QVBoxLayout(badge)
    b_layout.setContentsMargins(0, 0, 0, 0)
    b_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
    icon_label = QLabel()
    icon_label.setPixmap(get_svg_pixmap(get_svg_content(icon_name, is_dark), QSize(icon_size, icon_size)))
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    b_layout.addWidget(icon_label)
    return badge

def get_svg_pixmap(svg_str, size=QSize(24, 24)):
    pixmap = QPixmap(size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer = QSvgRenderer(svg_str.encode('utf-8'))
    renderer.render(painter)
    painter.end()
    return pixmap


class QuickActionButton(QPushButton):
    """A QuickActionButton that lifts on hover: its drop shadow's blur/offset
    animate outward, giving a tactile sense of elevation instead of relying
    purely on the QSS border-color swap."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("QuickActionButton")

        self._shadow = QGraphicsDropShadowEffect(self)
        self._shadow.setBlurRadius(16)
        self._shadow.setOffset(0, 3)
        self._shadow.setColor(QColor(0, 0, 0, 50))
        self.setGraphicsEffect(self._shadow)

        self._blur_anim = QPropertyAnimation(self._shadow, b"blurRadius", self)
        self._blur_anim.setDuration(160)
        self._blur_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._offset_anim = QPropertyAnimation(self._shadow, b"yOffset", self)
        self._offset_anim.setDuration(160)
        self._offset_anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _animate_to(self, blur, y_offset):
        self._blur_anim.stop()
        self._blur_anim.setStartValue(self._shadow.blurRadius())
        self._blur_anim.setEndValue(blur)
        self._blur_anim.start()

        self._offset_anim.stop()
        self._offset_anim.setStartValue(self._shadow.yOffset())
        self._offset_anim.setEndValue(y_offset)
        self._offset_anim.start()

    def enterEvent(self, event):
        self._animate_to(26, 8)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_to(16, 3)
        super().leaveEvent(event)

    def sizeHint(self):
        # QPushButton (via QAbstractButton) overrides sizeHint()/
        # minimumSizeHint() to compute size from the button's own text/icon
        # via QStyle -- it does NOT delegate to a child layout even when one
        # is set directly on the button (as _build_quick_action does with
        # badge/title/desc). Since this button never calls setText()/
        # setIcon(), the un-overridden sizeHint() reported a near-empty
        # size, so the outer quick_grid QHBoxLayout allocated far less
        # height than badge+title+desc actually need -- the inner QVBoxLayout
        # then had to compress its children into that undersized rect,
        # which is what produced the icon-badge-over-title overlap seen on
        # real-device testing (dev_notes.md Session N+6). Delegating to the
        # layout's own sizeHint fixes this at the source.
        if self.layout():
            return self.layout().sizeHint()
        return super().sizeHint()

    def minimumSizeHint(self):
        if self.layout():
            return self.layout().minimumSize()
        return super().minimumSizeHint()


class DragDropZone(QWidget):
    files_dropped = pyqtSignal(list)
    clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 16, 14, 16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)
        
        self.icon_badge_container = QWidget()
        badge_wrap_layout = QVBoxLayout(self.icon_badge_container)
        badge_wrap_layout.setContentsMargins(0, 0, 0, 2)
        badge_wrap_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_wrap_layout.addWidget(self.icon_label)
        layout.addWidget(self.icon_badge_container)
        
        self.text_label = QLabel("Drag & Drop Files Here", self)
        self.text_label.setObjectName("DragDropTitleLabel")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)
        
        self.subtext = QLabel("or click to select from PC", self)
        self.subtext.setObjectName("DragDropSubtextLabel")
        self.subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtext)

    def set_mode(self, is_pc_source: bool, is_dark: bool):
        if is_pc_source:
            self.text_label.setText("Drag & Drop Files Here")
            self.subtext.setText("or click to select from PC")
            self.icon_label.setPixmap(get_svg_pixmap(get_svg_content("pc", is_dark), QSize(26, 26)))
        else:
            self.text_label.setText("Select from Phone Storage")
            self.subtext.setText("Click to browse phone files & folders")
            self.icon_label.setPixmap(get_svg_pixmap(get_svg_content("phone", is_dark), QSize(26, 26)))

    def update_theme(self, is_dark, is_pc_source=True):
        self.set_mode(is_pc_source, is_dark)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty("dragActive", True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent):
        self.setProperty("dragActive", False)
        self.style().unpolish(self)
        self.style().polish(self)
        
        urls = event.mimeData().urls()
        paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
        if paths:
            self.files_dropped.emit(paths)


class StagedFileItemCard(QWidget):
    removed = pyqtSignal(int)

    def __init__(self, index: int, item: dict, is_dark: bool, parent=None):
        super().__init__(parent)
        self.index = index
        self.item = item
        self.setObjectName("StagedFileItemCard")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(8)

        icon_name = "folder" if item.get("is_dir") else "file"
        badge = make_icon_badge(icon_name, is_dark, size=26, icon_size=14)
        layout.addWidget(badge)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(1)

        display_name = item.get("name", "File")
        if len(display_name) > 28:
            display_name = display_name[:15] + "..." + display_name[-10:]
        name_label = QLabel(display_name)
        name_label.setObjectName("StagedFileName")
        name_label.setToolTip(item.get("path", ""))
        info_layout.addWidget(name_label)

        size_text = item.get("size_str", "")
        size_label = QLabel(size_text)
        size_label.setObjectName("StagedFileSize")
        info_layout.addWidget(size_label)

        layout.addLayout(info_layout, 1)

        remove_btn = QPushButton("✕")
        remove_btn.setObjectName("StagedFileRemoveBtn")
        remove_btn.setFixedSize(22, 22)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.setToolTip("Remove item")
        remove_btn.clicked.connect(lambda: self.removed.emit(self.index))
        layout.addWidget(remove_btn)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.onboarding_page_widget = None
        self.dashboard_page_widget = None
        self.history_page_widget = None
        self.settings_page_widget = None
        
        self.setWindowTitle("Warp Transfer")
        icon_path = get_resource_path("icon.ico")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setFixedSize(830 + 48, 630 + 48)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.config_path = os.path.join(os.path.expanduser('~'), 'warp_transfer_config.json')
        self.load_config()
        
        self.is_dark_mode = self.config.get("theme", "light") == "dark"
        
        self.adb_manager = AdbManager()
        self.drag_position = QPoint()
        self.active_coordinator = None
        self.is_paused = False
        self._transfer_start_time = 0
        self._transfer_context = {}  # direction/op_type for history logging
        self._transition_in_progress = False
        self._page_fade_anim = None
        self._theme_fade_anim = None

        self.transfer_direction = "pc_to_phone"
        self.transfer_mode = "copy"
        self.staged_items = []
        self.current_dest_path = "/sdcard/Download"
        self.dashboard_device_name = ""
        self.stepper_nodes = {}
        self.chip_buttons = []
        
        self.init_ui()
        self.apply_theme()
        
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_device_connection)
        
        if not self.adb_manager.is_adb_installed():
            self.show_downloader_page()
        else:
            self.adb_manager.start_server()
            self.show_onboarding_or_dashboard()
            self.check_timer.start(1500)

    def load_config(self):
        default_backup = os.path.join(os.path.expanduser('~'), 'Downloads', 'WarpTransferBackup')
        self.config = {
            "backup_destination": default_backup,
            "theme": "light",
            "conflict_mode": "ask",
            "throttle_kbps": 0,
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config.update(json.load(f))
            except Exception:
                pass

    def save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def _remember_known_device(self, device_id: str, friendly_name: str):
        if not device_id:
            return
        known = self.config.setdefault("known_devices", {})
        if known.get(device_id) != friendly_name:
            known[device_id] = friendly_name
            self.save_config()

    def init_ui(self):
        outer_wrapper = QWidget(self)
        self.setCentralWidget(outer_wrapper)
        outer_wrapper_layout = QVBoxLayout(outer_wrapper)
        outer_wrapper_layout.setContentsMargins(24, 24, 24, 24)
        outer_wrapper_layout.setSpacing(0)

        self.main_container = QWidget(outer_wrapper)
        self.main_container.setObjectName("MainWindowContainer")
        outer_wrapper_layout.addWidget(self.main_container)
        
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(50)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(18, 0, 12, 0)
        title_layout.setSpacing(10)
        
        self.logo_badge = QWidget()
        self.logo_badge.setObjectName("LogoBadge")
        self.logo_badge.setFixedSize(32, 32)
        logo_layout = QVBoxLayout(self.logo_badge)
        logo_layout.setContentsMargins(0, 0, 0, 0)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_logo = QLabel()
        self.title_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(self.title_logo)
        title_layout.addWidget(self.logo_badge)
        
        title_text = QLabel("Warp Transfer")
        title_text.setObjectName("TitleLabel")
        title_layout.addWidget(title_text)
        
        title_layout.addStretch()

        self.history_btn = QPushButton()
        self.history_btn.setObjectName("TitleBarButton")
        self.history_btn.setFixedSize(30, 30)
        self.history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_btn.clicked.connect(self.show_history_page)
        title_layout.addWidget(self.history_btn)

        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("TitleBarButton")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.clicked.connect(self.show_settings_page)
        title_layout.addWidget(self.settings_btn)
        
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("TitleBarButton")
        self.theme_btn.setFixedSize(30, 30)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.clicked.connect(self.toggle_theme)
        title_layout.addWidget(self.theme_btn)
        
        self.min_btn = QPushButton()
        self.min_btn.setObjectName("TitleBarButton")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.min_btn)
        
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.clicked.connect(self.close_app)
        title_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(self.title_bar)
        
        self.stacked_pages = QStackedWidget(self)
        main_layout.addWidget(self.stacked_pages)
        
        self.title_bar.mousePressEvent = self.title_bar_press
        self.title_bar.mouseMoveEvent = self.title_bar_move

    def apply_theme(self):
        app = QApplication.instance()
        if app and not getattr(app, "_warp_stylesheet_loaded", False):
            app.setStyleSheet(APP_STYLE)
            app._warp_stylesheet_loaded = True

        self._tag_theme(self)

        bg_color = "#0C0C0E" if self.is_dark_mode else "#F2F2F7"
        border_color = "#1E1E24" if self.is_dark_mode else "#D1D1D6"
        self.main_container.setStyleSheet(f"""
            #MainWindowContainer {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 16px;
            }}
        """)
        
        add_shadow(self.main_container, blur=40, y_offset=10, alpha=110)
        
        self.title_logo.setPixmap(get_svg_pixmap(get_svg_content("zap", self.is_dark_mode), QSize(18, 18)))
        self.history_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("history", self.is_dark_mode), QSize(15, 15))))
        self.settings_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("settings", self.is_dark_mode), QSize(15, 15))))
        self.theme_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("sun" if self.is_dark_mode else "moon", self.is_dark_mode), QSize(14, 14))))
        self.min_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("minimize", self.is_dark_mode), QSize(12, 12))))
        self.close_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("close", self.is_dark_mode), QSize(12, 12))))

        if self.dashboard_page_widget and hasattr(self, "drop_zone") and self.drop_zone is not None:
            self.drop_zone.update_theme(self.is_dark_mode, self.transfer_direction == "pc_to_phone")
            self.device_icon_badge_refresh()

    def _tag_theme(self, widget):
        tag_theme_recursive(widget, self.is_dark_mode)

    def _fade_transition(self, target):
        self._transition_in_progress = True

        def _done():
            self._transition_in_progress = False

        self._page_fade_anim = fade_to_page(self.stacked_pages, target, on_finished=_done)

    def device_icon_badge_refresh(self):
        if hasattr(self, "device_icon") and self.device_icon is not None:
            self.device_icon.setPixmap(get_svg_pixmap(get_svg_content("phone", self.is_dark_mode), QSize(17, 17)))

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

        self._theme_fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self._theme_fade_anim.setDuration(120)
        self._theme_fade_anim.setStartValue(0.85)
        self._theme_fade_anim.setEndValue(1.0)
        self._theme_fade_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._theme_fade_anim.start()

        self.config["theme"] = "dark" if self.is_dark_mode else "light"
        QTimer.singleShot(0, self.save_config)

    def close_app(self):
        if self.active_coordinator:
            self.active_coordinator.cancel()
            self.active_coordinator.wait()
        self.adb_manager.kill_server()
        self.close()

    def title_bar_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def title_bar_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    # Setup the download platform-tools page
    def show_downloader_page(self):
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(40, 40, 40, 40)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setObjectName("CardContainer")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        icon_badge = make_icon_badge("download", self.is_dark_mode, size=72, icon_size=36)
        layout.addWidget(icon_badge, 0, Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Downloading Android Platform Tools", card)
        title.setObjectName("HeaderLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)
        
        desc = QLabel(
            "Warp Transfer requires Google's official Android platform tools to run high-speed transfers.\n"
            "This download happens only once and will finish shortly.",
            card
        )
        desc.setObjectName("SubHeaderLabel")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        self.download_bar = QProgressBar(card)
        self.download_bar.setFixedHeight(12)
        self.download_bar.setRange(0, 100)
        self.download_bar.setValue(0)
        layout.addWidget(self.download_bar)
        
        self.download_status = QLabel("Connecting...", card)
        self.download_status.setObjectName("PathLabel")
        self.download_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.download_status)

        # Retry button -- hidden until a download actually fails. Previously
        # a failed download left the person stuck on this screen forever
        # with no way to try again short of restarting the whole app.
        self.download_retry_btn = QPushButton("Retry Download", card)
        self.download_retry_btn.setObjectName("PrimaryButton")
        self.download_retry_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.download_retry_btn.clicked.connect(self.retry_download)
        self.download_retry_btn.setVisible(False)
        layout.addWidget(self.download_retry_btn)

        outer_layout.addWidget(card)
        add_shadow(card, blur=28, y_offset=8, alpha=70)
        
        idx = self.stacked_pages.addWidget(page)
        self.stacked_pages.setCurrentIndex(idx)
        self._tag_theme(page)
        
        self._start_download_worker()

    def _start_download_worker(self):
        """Shared by the initial download attempt and retry_download() so
        both paths reset to the exact same clean state and wire up signals
        identically -- avoids the two call sites silently drifting apart."""
        self.download_bar.setRange(0, 100)
        self.download_bar.setValue(0)
        self.download_status.setText("Connecting...")
        self.download_status.setObjectName("PathLabel")
        self.download_status.setStyleSheet("")
        self.download_retry_btn.setVisible(False)

        self.download_worker = self.adb_manager.start_download()
        self.download_worker.progress.connect(self.update_download_progress)
        self.download_worker.finished.connect(self.on_download_finished)
        self.download_worker.start()

    def retry_download(self):
        self._start_download_worker()

    def update_download_progress(self, current, total):
        if total > 0:
            # Real Content-Length available -- normal determinate progress.
            if self.download_bar.maximum() == 0:
                self.download_bar.setRange(0, 100)
            pct = int((current / total) * 100)
            self.download_bar.setValue(pct)
            mb_cur = current / (1024 * 1024)
            mb_tot = total / (1024 * 1024)
            self.download_status.setText(f"Downloaded {mb_cur:.1f}MB of {mb_tot:.1f}MB ({pct}%)")
        else:
            # No Content-Length header from the server -- previously this
            # branch was simply skipped entirely, so the bar and status text
            # stayed frozen on "Connecting..." for the whole download even
            # though bytes were actually arriving. Switch the bar to
            # indeterminate ("busy") mode and show live downloaded bytes
            # instead, so it's visibly moving rather than looking hung.
            self.download_bar.setRange(0, 0)
            mb_cur = current / (1024 * 1024)
            self.download_status.setText(f"Downloading... {mb_cur:.1f}MB so far (size unknown)")

    def on_download_finished(self, success, message):
        if success:
            self.adb_manager.start_server()
            self.show_onboarding_or_dashboard()
            self.check_timer.start(1500)
        else:
            self.download_bar.setRange(0, 100)
            self.download_bar.setValue(0)
            self.download_status.setText(f"Download failed: {message}")
            self.download_status.setObjectName("DangerButton")
            self.download_status.setStyleSheet("color: #FF453A; font-weight: 600; background: transparent; border: none;")
            self.download_retry_btn.setVisible(True)

    # Show dashboard or onboarding wizard depending on device status
    def show_onboarding_or_dashboard(self):
        status, device = self.adb_manager.check_devices()

        if status == "connected":
            self._remember_known_device(self.adb_manager.current_device_id, device)
            self.show_dashboard_page(device)
        else:
            self.show_onboarding_page()

    def check_device_connection(self):
        # Phase 2 (motion): skip checking/updating connection status while
        # a transition is actively animating.
        if self._transition_in_progress:
            return

        # Triggered by timer
        status, device = self.adb_manager.check_devices()
        
        curr_page = self.stacked_pages.currentWidget()
        if self.onboarding_page_widget and curr_page == self.onboarding_page_widget:
            # Keep the wizard's live status banner in sync every tick, not just on the
            # connected -> dashboard transition below. Confirmed missing before this fix:
            # OnboardingWizard.update_connection_status() was fully built and documented as
            # being "called by MainWindow every poll tick" but nothing ever actually called
            # it -- unauthorized/multiple/offline never reached the UI.
            #
            # known_devices is now passed here too (previously omitted) -- without it,
            # the reconnect view (Phase 4) would show correctly for exactly one frame
            # right when show_onboarding_page() first ran, then immediately flip back
            # to the full first-time wizard on THIS method's very next 1.5s tick, since
            # update_connection_status()'s known_devices arg would silently default to
            # None/{} here and override the correct earlier call.
            self.onboarding_page_widget.update_connection_status(status, device, self.config.get("known_devices", {}))
        if status == "connected" and self.onboarding_page_widget and curr_page == self.onboarding_page_widget:
            # Transition to dashboard smoothly
            self._remember_known_device(self.adb_manager.current_device_id, device)
            self.show_dashboard_page(device)
        elif status != "connected" and self.dashboard_page_widget and curr_page == self.dashboard_page_widget:
            # Transition back to onboarding setup
            self.show_onboarding_page()

    # Create & display Onboarding View
    def show_onboarding_page(self):
        if self.onboarding_page_widget:
            status, device = self.adb_manager.check_devices()
            # FIX: this branch was missing the known_devices arg that the
            # "build fresh" branch below (and check_device_connection's own
            # poll-tick call) both correctly pass -- found on a fresh
            # re-verification pass, not caught by the Session N+11 fix to
            # check_device_connection. This branch runs any time the wizard
            # widget already exists and is just being re-shown (e.g. a
            # second+ disconnect in the same app session reuses the cached
            # instance), so without this it would flicker the reconnect view
            # back to the full first-time wizard for one frame until the
            # next 1.5s poll tick corrected it.
            self.onboarding_page_widget.update_connection_status(status, device, self.config.get("known_devices", {}))
            self._fade_transition(self.onboarding_page_widget)
            return
            
        self.onboarding_page_widget = OnboardingWizard(self.adb_manager)
        self.onboarding_page_widget.choose_device_clicked.connect(self.handle_choose_device)
        self.onboarding_page_widget.connect_wirelessly_clicked.connect(self.open_wireless_dialog)
        # Wire the wizard's "Finish" button (emits `finished` on step 4) --
        # previously unconnected, so clicking Finish did nothing at all.
        self.onboarding_page_widget.finished.connect(self.show_onboarding_or_dashboard)
        self.stacked_pages.addWidget(self.onboarding_page_widget)
        # Show real status immediately rather than leaving the banner blank until the
        # first timer tick fires.
        status, device = self.adb_manager.check_devices()
        self.onboarding_page_widget.update_connection_status(status, device, self.config.get("known_devices", {}))
        self._fade_transition(self.onboarding_page_widget)
        self._tag_theme(self.onboarding_page_widget)

    def handle_choose_device(self):
        """Wired to OnboardingWizard's 'Choose Device' button, shown when
        check_devices() reports 'multiple'. Lets the user pick a specific
        device instead of being stuck until all-but-one are unplugged."""
        devices = self.adb_manager.list_all_devices()
        chosen_id = DevicePickerDialog.ask(devices, self.is_dark_mode, self)
        if chosen_id:
            self.adb_manager.set_target_device(chosen_id)
            self.show_onboarding_or_dashboard()

    def open_wireless_dialog(self):
        dlg = WirelessConnectDialog(self.adb_manager, self.is_dark_mode, self)
        dlg.exec()
        # Re-check immediately in case a connect/pair succeeded, rather than
        # waiting up to 1.5s for the next poll tick.
        self.show_onboarding_or_dashboard()

    # ------------------------------------------------------------------
    # Settings page
    # ------------------------------------------------------------------

    def show_settings_page(self):
        # FIX (real-device report: navigating to Settings mid-transfer, then
        # Back, silently killed the transfer and dropped back to a fresh
        # dashboard with a stray "Transfer Failed"): return_to_dashboard()
        # unconditionally rebuilt/resumed polling regardless of whether a
        # TransferCoordinator was still actually running in the background.
        # Simplest correct fix is upstream of that: don't let Settings/
        # History be entered at all while a transfer is active, so there's
        # nothing for Back to tear down in the first place. The titlebar
        # buttons are also disabled for the same window (see
        # start_transfer_ui/on_transfer_finished) so this is a defensive
        # backstop, not the only guard.
        if self.active_coordinator is not None:
            return
        # Drop the previous settings page instance rather than stacking a
        # fresh one on top every time the titlebar button is clicked --
        # otherwise repeated visits silently accumulate hidden QWidgets in
        # the QStackedWidget for the lifetime of the app.
        if self.settings_page_widget is not None:
            self.stacked_pages.removeWidget(self.settings_page_widget)
            self.settings_page_widget.deleteLater()
            self.settings_page_widget = None

        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(30, 25, 30, 25)
        outer_layout.setSpacing(16)

        header_row = QHBoxLayout()
        back_btn = QPushButton()
        back_btn.setObjectName("TitleBarButton")
        back_btn.setFixedSize(30, 30)
        back_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("back", self.is_dark_mode), QSize(15, 15))))
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.return_to_dashboard)
        header_row.addWidget(back_btn)
        title = QLabel("Settings", page)
        title.setObjectName("HeaderLabel")
        header_row.addWidget(title)
        header_row.addStretch()
        outer_layout.addLayout(header_row)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)

        # Backup destination
        dest_card = self._settings_card("Backup Destination", "Where phone-to-PC backups are saved.")
        dest_row = QHBoxLayout()
        self.settings_dest_label = QLabel(self.get_truncated_dest_path())
        self.settings_dest_label.setObjectName("PathLabel")
        dest_row.addWidget(self.settings_dest_label, 1)
        change_btn = QPushButton("Change...")
        change_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_btn.clicked.connect(self.change_backup_destination)
        dest_row.addWidget(change_btn)
        dest_card.layout().addLayout(dest_row)
        content_layout.addWidget(dest_card)

        # Conflict resolution default
        conflict_card = self._settings_card("File Conflicts", "What to do when a transfer target already has a file with that name.")
        conflict_row = QHBoxLayout()
        conflict_row.setSpacing(8)
        self.conflict_buttons = {}
        for mode, label in [("ask", "Ask Every Time"), ("skip", "Skip"), ("overwrite", "Overwrite"), ("rename", "Keep Both")]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setChecked(self.config.get("conflict_mode", "ask") == mode)
            btn.clicked.connect(lambda checked, m=mode: self._set_conflict_mode(m))
            conflict_row.addWidget(btn)
            self.conflict_buttons[mode] = btn
        conflict_card.layout().addLayout(conflict_row)
        content_layout.addWidget(conflict_card)

        # Speed throttle
        throttle_card = self._settings_card("Transfer Speed Limit", "Cap transfer bandwidth, e.g. to keep the connection responsive for other tasks. Unlimited uses the fastest multi-threaded path.")
        throttle_row = QHBoxLayout()
        throttle_row.setSpacing(8)
        self.throttle_buttons = {}
        for kbps, label in [(0, "Unlimited"), (512, "512 KB/s"), (2048, "2 MB/s"), (10240, "10 MB/s")]:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setChecked(self.config.get("throttle_kbps", 0) == kbps)
            btn.clicked.connect(lambda checked, k=kbps: self._set_throttle(k))
            throttle_row.addWidget(btn)
            self.throttle_buttons[kbps] = btn
        throttle_card.layout().addLayout(throttle_row)
        content_layout.addWidget(throttle_card)

        # Wireless connection
        wireless_card = self._settings_card("Wireless Connection", "Pair or reconnect to a device over Wi-Fi instead of USB.")
        wireless_btn = QPushButton("Connect Wirelessly")
        wireless_btn.setObjectName("PrimaryButton")
        wireless_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        wireless_btn.clicked.connect(self.open_wireless_dialog)
        wireless_card.layout().addWidget(wireless_btn)
        content_layout.addWidget(wireless_card)

        content_layout.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self.settings_page_widget = page
        idx = self.stacked_pages.addWidget(page)
        self._fade_transition(idx)
        self._tag_theme(page)

    def _settings_card(self, title_text, desc_text) -> QWidget:
        card = QWidget()
        card.setObjectName("InnerCard")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(8)
        title = QLabel(title_text, card)
        title.setObjectName("QuickActionButtonTitle")
        layout.addWidget(title)
        desc = QLabel(desc_text, card)
        desc.setObjectName("QuickActionButtonDesc")
        desc.setWordWrap(True)
        layout.addWidget(desc)
        return card

    def _set_conflict_mode(self, mode):
        self.config["conflict_mode"] = mode
        self.save_config()
        for m, btn in self.conflict_buttons.items():
            btn.setChecked(m == mode)

    def _set_throttle(self, kbps):
        self.config["throttle_kbps"] = kbps
        self.save_config()
        for k, btn in self.throttle_buttons.items():
            btn.setChecked(k == kbps)

    # ------------------------------------------------------------------
    # History page
    # ------------------------------------------------------------------

    def show_history_page(self):
        # Same mid-transfer guard as show_settings_page -- see its comment.
        if self.active_coordinator is not None:
            return
        # Same reasoning as show_settings_page: drop the previous instance
        # instead of stacking a new hidden widget on every "History" click.
        if self.history_page_widget is not None:
            self.stacked_pages.removeWidget(self.history_page_widget)
            self.history_page_widget.deleteLater()
            self.history_page_widget = None

        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(30, 25, 30, 25)
        outer_layout.setSpacing(16)

        header_row = QHBoxLayout()
        back_btn = QPushButton()
        back_btn.setObjectName("TitleBarButton")
        back_btn.setFixedSize(30, 30)
        back_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("back", self.is_dark_mode), QSize(15, 15))))
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.clicked.connect(self.return_to_dashboard)
        header_row.addWidget(back_btn)
        title = QLabel("Transfer History", page)
        title.setObjectName("HeaderLabel")
        header_row.addWidget(title)
        header_row.addStretch()
        clear_btn = QPushButton("Clear")
        clear_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("trash", self.is_dark_mode), QSize(13, 13))))
        clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_btn.clicked.connect(self.clear_history_and_refresh)
        header_row.addWidget(clear_btn)
        outer_layout.addLayout(header_row)

        entries = history_manager.get_entries()

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)

        if not entries:
            empty = QLabel("No transfers yet. Completed transfers will show up here.")
            empty.setObjectName("SubHeaderLabel")
            empty.setWordWrap(True)
            content_layout.addWidget(empty)
        else:
            for entry in entries:
                content_layout.addWidget(self._history_row(entry))

        content_layout.addStretch()
        scroll.setWidget(content)
        outer_layout.addWidget(scroll)

        self.history_page_widget = page
        idx = self.stacked_pages.addWidget(page)
        self._fade_transition(idx)
        self._tag_theme(page)

    def _history_row(self, entry: dict) -> QWidget:
        row = QWidget()
        row.setObjectName("InnerCard")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(14, 10, 14, 10)
        layout.setSpacing(12)

        icon_name = "check" if entry.get("success") else "alert"
        badge = make_icon_badge(icon_name, self.is_dark_mode, size=32, icon_size=16)
        layout.addWidget(badge)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        direction_label = "Phone \u2192 PC" if entry.get("direction") == "phone_to_pc" else "PC \u2192 Phone"
        op_label = "Moved" if entry.get("operation_type") == "move" else "Copied"
        title = QLabel(f"{op_label} {entry.get('file_count', 0)} file(s) \u2022 {direction_label}")
        title.setObjectName("TransferDetailLabel")
        info_layout.addWidget(title)

        ts = entry.get("timestamp", 0)
        when = time.strftime("%b %d, %Y \u2022 %I:%M %p", time.localtime(ts)) if ts else ""
        size_str = history_manager.format_bytes(entry.get("total_bytes", 0))
        dur_str = history_manager.format_duration(entry.get("duration_seconds", 0))
        subtitle = QLabel(f"{when}  \u2022  {size_str}  \u2022  {dur_str}")
        subtitle.setObjectName("TransferFileLabel")
        info_layout.addWidget(subtitle)

        layout.addLayout(info_layout, 1)
        return row

    def clear_history_and_refresh(self):
        history_manager.clear_history()
        self.show_history_page()

    # --- Workspace Staging & Direction Methods ---

    def _calc_folder_size(self, path: str) -> int:
        total = 0
        try:
            for root, _, files in os.walk(path):
                for f in files:
                    fp = os.path.join(root, f)
                    if not os.path.islink(fp):
                        try:
                            total += os.path.getsize(fp)
                        except OSError:
                            pass
        except Exception:
            pass
        return total

    def add_pc_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Transfer")
        if not files:
            return
        existing = {item["path"] for item in self.staged_items}
        for f in files:
            if f not in existing:
                sz = 0
                try:
                    sz = os.path.getsize(f)
                except Exception:
                    pass
                self.staged_items.append({
                    "path": f,
                    "name": os.path.basename(f),
                    "size": sz,
                    "size_str": history_manager.format_bytes(sz),
                    "is_dir": False
                })
                existing.add(f)
        self.refresh_workspace_ui()

    def add_pc_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Transfer")
        if not folder:
            return
        existing = {item["path"] for item in self.staged_items}
        if folder not in existing:
            sz = self._calc_folder_size(folder)
            self.staged_items.append({
                "path": folder,
                "name": os.path.basename(folder) or folder,
                "size": sz,
                "size_str": history_manager.format_bytes(sz) if sz > 0 else "Folder",
                "is_dir": True
            })
        self.refresh_workspace_ui()

    def browse_phone_files(self):
        selected = PhoneBrowserDialog.ask(self.adb_manager, self.is_dark_mode, self)
        if not selected:
            return
        existing = {item["path"] for item in self.staged_items}
        for p in selected:
            if p not in existing:
                name = p.rstrip("/").split("/")[-1] or p
                self.staged_items.append({
                    "path": p,
                    "name": name,
                    "size": 0,
                    "size_str": "Phone Item",
                    "is_dir": False
                })
                existing.add(p)
        self.refresh_workspace_ui()

    def remove_staged_item(self, idx: int):
        if 0 <= idx < len(self.staged_items):
            self.staged_items.pop(idx)
            self.refresh_workspace_ui()

    def clear_staged_items(self):
        self.staged_items.clear()
        self.refresh_workspace_ui()

    def handle_drag_dropped_files(self, paths):
        if self.transfer_direction != "pc_to_phone":
            self.set_transfer_direction("pc_to_phone")
        existing = {item["path"] for item in self.staged_items}
        for p in paths:
            if p not in existing:
                is_dir = os.path.isdir(p)
                sz = self._calc_folder_size(p) if is_dir else (os.path.getsize(p) if os.path.exists(p) else 0)
                self.staged_items.append({
                    "path": p,
                    "name": os.path.basename(p) or p,
                    "size": sz,
                    "size_str": history_manager.format_bytes(sz) if (sz > 0 or not is_dir) else "Folder",
                    "is_dir": is_dir
                })
                existing.add(p)
        self.refresh_workspace_ui()

    def set_transfer_direction(self, direction: str):
        if self.transfer_direction == direction:
            return
        self.transfer_direction = direction
        self.staged_items.clear()
        if direction == "pc_to_phone":
            self.current_dest_path = "/sdcard/Download"
        else:
            self.current_dest_path = self.config.get("backup_destination", os.path.join(os.path.expanduser('~'), 'Downloads', 'WarpTransferBackup'))
        if self.dashboard_device_name:
            self.show_dashboard_page(self.dashboard_device_name)

    def toggle_transfer_direction(self):
        new_dir = "phone_to_pc" if self.transfer_direction == "pc_to_phone" else "pc_to_phone"
        self.set_transfer_direction(new_dir)

    def set_dest_quick_chip(self, path: str):
        self.current_dest_path = path
        self.refresh_destination_ui()

    def change_destination_folder(self):
        if self.transfer_direction == "pc_to_phone":
            chosen = PhoneFolderPickerDialog.ask(self.adb_manager, self.is_dark_mode, self.current_dest_path, self)
            if chosen:
                self.current_dest_path = chosen
                self.refresh_destination_ui()
        else:
            chosen = QFileDialog.getExistingDirectory(self, "Select Destination Folder", self.current_dest_path)
            if chosen:
                self.current_dest_path = os.path.abspath(chosen)
                self.config["backup_destination"] = self.current_dest_path
                self.save_config()
                self.refresh_destination_ui()

    def set_transfer_mode(self, mode: str):
        self.transfer_mode = mode
        self.refresh_mode_ui()

    def get_staged_total_size(self) -> int:
        return sum(item.get("size", 0) for item in self.staged_items)

    def refresh_workspace_ui(self):
        if not hasattr(self, "staged_list_layout"):
            return
        
        while self.staged_list_layout.count():
            child = self.staged_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        has_items = len(self.staged_items) > 0
        self.drop_zone_container.setVisible(not has_items)
        self.staged_list_scroll.setVisible(has_items)
        self.staging_summary_bar.setVisible(has_items)

        if has_items:
            for idx, item in enumerate(self.staged_items):
                card = StagedFileItemCard(idx, item, self.is_dark_mode, self.staged_list_widget)
                card.removed.connect(self.remove_staged_item)
                self.staged_list_layout.addWidget(card)
                self._tag_theme(card)
            self.staged_list_layout.addStretch()

            total_bytes = self.get_staged_total_size()
            size_str = history_manager.format_bytes(total_bytes) if total_bytes > 0 else ""
            summary_text = f"{len(self.staged_items)} item(s)" + (f" • {size_str}" if size_str else "")
            self.staging_summary_pill.setText(summary_text)

        can_transfer = has_items and (self.transfer_mode in ["copy", "move"])
        self.start_transfer_btn.setEnabled(can_transfer)
        if can_transfer:
            self.start_transfer_btn.setText(f"Start Transfer ({len(self.staged_items)}) ➔")
        else:
            self.start_transfer_btn.setText("Start Transfer ➔")

    def refresh_destination_ui(self):
        if hasattr(self, "dest_path_label"):
            disp = self.current_dest_path
            if len(disp) > 38:
                disp = disp[:18] + "..." + disp[-18:]
            self.dest_path_label.setText(disp)
            self.dest_path_label.setToolTip(self.current_dest_path)

        for btn, chip_path in self.chip_buttons:
            is_active = (self.current_dest_path.rstrip("/\\") == chip_path.rstrip("/\\"))
            btn.setProperty("active", is_active)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def refresh_mode_ui(self):
        if hasattr(self, "copy_mode_btn") and hasattr(self, "move_mode_btn"):
            self.copy_mode_btn.setChecked(self.transfer_mode == "copy")
            self.move_mode_btn.setChecked(self.transfer_mode == "move")
            if hasattr(self, "move_warning_label"):
                self.move_warning_label.setVisible(self.transfer_mode == "move")
        self.refresh_workspace_ui()

    # --- Dashboard Page Construction ---

    def show_dashboard_page(self, device_name):
        self.dashboard_device_name = device_name
        if self.dashboard_page_widget is not None:
            self.stacked_pages.removeWidget(self.dashboard_page_widget)
            self.dashboard_page_widget.deleteLater()
            self.dashboard_page_widget = None

        self.dashboard_page_widget = QWidget()
        layout = QVBoxLayout(self.dashboard_page_widget)
        layout.setContentsMargins(22, 14, 22, 16)
        layout.setSpacing(10)
        
        # 1. Connected Device Header Bar
        header = QWidget()
        header.setObjectName("InnerCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(14, 8, 14, 8)
        header_layout.setSpacing(10)
        
        device_icon_badge = QWidget()
        device_icon_badge.setObjectName("IconBadge")
        device_icon_badge.setFixedSize(32, 32)
        dib_layout = QVBoxLayout(device_icon_badge)
        dib_layout.setContentsMargins(0, 0, 0, 0)
        dib_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.device_icon = QLabel()
        self.device_icon.setPixmap(get_svg_pixmap(get_svg_content("phone", self.is_dark_mode), QSize(17, 17)))
        dib_layout.addWidget(self.device_icon)
        header_layout.addWidget(device_icon_badge)
        
        device_info = QVBoxLayout()
        device_info.setSpacing(1)
        device_title = QLabel(device_name)
        device_title.setObjectName("DeviceTitleLabel")
        device_status = QLabel("Connected via USB Debugging (Max Speed)")
        device_status.setObjectName("SuccessStatusLabel")
        device_info.addWidget(device_title)
        device_info.addWidget(device_status)
        header_layout.addLayout(device_info)
        header_layout.addStretch()

        # Top Direction Segmented Toggle Bar
        dir_bar = QWidget()
        dir_bar.setObjectName("DirectionSegmentContainer")
        dir_bar_layout = QHBoxLayout(dir_bar)
        dir_bar_layout.setContentsMargins(3, 3, 3, 3)
        dir_bar_layout.setSpacing(4)

        self.pc_to_phone_btn = QPushButton("💻 PC ➔ 📱 Phone")
        self.pc_to_phone_btn.setObjectName("DirectionSegmentBtn")
        self.pc_to_phone_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.pc_to_phone_btn.setProperty("active", self.transfer_direction == "pc_to_phone")
        self.pc_to_phone_btn.clicked.connect(lambda: self.set_transfer_direction("pc_to_phone"))
        dir_bar_layout.addWidget(self.pc_to_phone_btn)

        self.dir_swap_btn = QPushButton("⇄")
        self.dir_swap_btn.setObjectName("DirectionSwapBtn")
        self.dir_swap_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dir_swap_btn.setToolTip("Swap Transfer Direction")
        self.dir_swap_btn.clicked.connect(self.toggle_transfer_direction)
        dir_bar_layout.addWidget(self.dir_swap_btn)

        self.phone_to_pc_btn = QPushButton("📱 Phone ➔ 💻 PC")
        self.phone_to_pc_btn.setObjectName("DirectionSegmentBtn")
        self.phone_to_pc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.phone_to_pc_btn.setProperty("active", self.transfer_direction == "phone_to_pc")
        self.phone_to_pc_btn.clicked.connect(lambda: self.set_transfer_direction("phone_to_pc"))
        dir_bar_layout.addWidget(self.phone_to_pc_btn)

        header_layout.addWidget(dir_bar)
        layout.addWidget(header)
        add_shadow(header, blur=14, y_offset=2, alpha=50)

        # 2. Split Two-Column Transfer Workspace
        split_layout = QHBoxLayout()
        split_layout.setSpacing(12)

        is_pc_src = (self.transfer_direction == "pc_to_phone")

        # --- LEFT COLUMN (SOURCE) ---
        left_col = QWidget()
        left_col.setObjectName("SplitColumnCard")
        left_layout = QVBoxLayout(left_col)
        left_layout.setContentsMargins(14, 12, 14, 12)
        left_layout.setSpacing(8)

        # Left Column Header
        left_header = QHBoxLayout()
        left_header.setSpacing(8)
        src_icon = "pc" if is_pc_src else "phone"
        left_header.addWidget(make_icon_badge(src_icon, self.is_dark_mode, size=28, icon_size=15))
        src_title = QLabel("Source: PC" if is_pc_src else "Source: Phone")
        src_title.setObjectName("ColumnHeaderTitle")
        left_header.addWidget(src_title)
        left_header.addStretch()

        src_badge = QLabel("SOURCE")
        src_badge.setObjectName("ColumnRoleBadge")
        src_badge.setFixedHeight(22)
        src_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        src_badge.setProperty("roleType", "source")
        left_header.addWidget(src_badge)
        left_layout.addLayout(left_header)

        # Staging: Empty DropZone Container
        self.drop_zone_container = QWidget()
        dzc_layout = QVBoxLayout(self.drop_zone_container)
        dzc_layout.setContentsMargins(0, 0, 0, 0)
        dzc_layout.setSpacing(8)

        self.drop_zone = DragDropZone(self)
        self.drop_zone.update_theme(self.is_dark_mode, is_pc_src)
        self.drop_zone.files_dropped.connect(self.handle_drag_dropped_files)
        if is_pc_src:
            self.drop_zone.clicked.connect(self.add_pc_files)
        else:
            self.drop_zone.clicked.connect(self.browse_phone_files)
        dzc_layout.addWidget(self.drop_zone, 1)

        # Action Buttons when Empty
        empty_actions = QHBoxLayout()
        empty_actions.setSpacing(8)
        if is_pc_src:
            add_files_btn = QPushButton("+ Add Files", self)
            add_files_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_files_btn.clicked.connect(self.add_pc_files)
            empty_actions.addWidget(add_files_btn)

            add_folder_btn = QPushButton("+ Add Folder", self)
            add_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_folder_btn.clicked.connect(self.add_pc_folder)
            empty_actions.addWidget(add_folder_btn)
        else:
            browse_phone_btn = QPushButton("+ Browse Phone Files", self)
            browse_phone_btn.setObjectName("PrimaryButton")
            browse_phone_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            browse_phone_btn.clicked.connect(self.browse_phone_files)
            empty_actions.addWidget(browse_phone_btn)
        dzc_layout.addLayout(empty_actions)
        left_layout.addWidget(self.drop_zone_container, 1)

        # Staging: Populated Scroll Area
        self.staged_list_scroll = QScrollArea()
        self.staged_list_scroll.setObjectName("StagedFileListScroll")
        self.staged_list_scroll.setWidgetResizable(True)
        self.staged_list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.staged_list_widget = QWidget()
        self.staged_list_layout = QVBoxLayout(self.staged_list_widget)
        self.staged_list_layout.setContentsMargins(2, 2, 2, 2)
        self.staged_list_layout.setSpacing(6)
        self.staged_list_scroll.setWidget(self.staged_list_widget)
        left_layout.addWidget(self.staged_list_scroll, 1)

        # Staging Summary & Add More Bar
        self.staging_summary_bar = QWidget()
        ssb_layout = QVBoxLayout(self.staging_summary_bar)
        ssb_layout.setContentsMargins(0, 0, 0, 0)
        ssb_layout.setSpacing(6)

        ssb_top = QHBoxLayout()
        ssb_top.setSpacing(6)
        if is_pc_src:
            add_more_btn = QPushButton("+ Add Files", self)
            add_more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            add_more_btn.clicked.connect(self.add_pc_files)
            ssb_top.addWidget(add_more_btn)

            add_more_folder = QPushButton("+ Folder", self)
            add_more_folder.setCursor(Qt.CursorShape.PointingHandCursor)
            add_more_folder.clicked.connect(self.add_pc_folder)
            ssb_top.addWidget(add_more_folder)
        else:
            add_more_phone = QPushButton("+ Browse Phone", self)
            add_more_phone.setCursor(Qt.CursorShape.PointingHandCursor)
            add_more_phone.clicked.connect(self.browse_phone_files)
            ssb_top.addWidget(add_more_phone)

        clear_all_btn = QPushButton("Clear All", self)
        clear_all_btn.setObjectName("DangerButton")
        clear_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        clear_all_btn.clicked.connect(self.clear_staged_items)
        ssb_top.addWidget(clear_all_btn)
        ssb_layout.addLayout(ssb_top)

        self.staging_summary_pill = QLabel("0 items")
        self.staging_summary_pill.setObjectName("StagingSummaryPill")
        self.staging_summary_pill.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ssb_layout.addWidget(self.staging_summary_pill)

        left_layout.addWidget(self.staging_summary_bar)
        split_layout.addWidget(left_col, 1)

        # --- RIGHT COLUMN (DESTINATION) ---
        right_col = QWidget()
        right_col.setObjectName("SplitColumnCard")
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(14, 12, 14, 12)
        right_layout.setSpacing(10)

        # Right Column Header
        right_header = QHBoxLayout()
        right_header.setSpacing(8)
        dest_icon = "phone" if is_pc_src else "pc"
        right_header.addWidget(make_icon_badge(dest_icon, self.is_dark_mode, size=28, icon_size=15))
        dest_title = QLabel("Destination: Phone" if is_pc_src else "Destination: PC")
        dest_title.setObjectName("ColumnHeaderTitle")
        right_header.addWidget(dest_title)
        right_header.addStretch()

        dest_badge = QLabel("DESTINATION")
        dest_badge.setObjectName("ColumnRoleBadge")
        dest_badge.setFixedHeight(22)
        dest_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dest_badge.setProperty("roleType", "dest")
        right_header.addWidget(dest_badge)
        right_layout.addLayout(right_header)

        # Landing Folder Card
        dest_card = QWidget()
        dest_card.setObjectName("InnerCard")
        dc_layout = QVBoxLayout(dest_card)
        dc_layout.setContentsMargins(12, 10, 12, 10)
        dc_layout.setSpacing(6)

        dc_head = QHBoxLayout()
        dc_head.setSpacing(8)
        dc_head.addWidget(make_icon_badge("folder", self.is_dark_mode, size=24, icon_size=13))
        dc_title = QLabel("Landing Directory:")
        dc_title.setObjectName("SubHeaderLabel")
        dc_head.addWidget(dc_title)
        dc_head.addStretch()
        dc_layout.addLayout(dc_head)

        self.dest_path_label = QLabel(self.current_dest_path)
        self.dest_path_label.setObjectName("PathLabel")
        self.dest_path_label.setWordWrap(True)
        dc_layout.addWidget(self.dest_path_label)

        browse_dest_btn = QPushButton("Change Folder...", self)
        browse_dest_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_dest_btn.clicked.connect(self.change_destination_folder)
        dc_layout.addWidget(browse_dest_btn)
        right_layout.addWidget(dest_card)

        # Quick Location Chips
        chips_section = QVBoxLayout()
        chips_section.setSpacing(6)
        chips_title = QLabel("Quick Locations:")
        chips_title.setObjectName("SubHeaderLabel")
        chips_section.addWidget(chips_title)

        self.chip_buttons = []
        chips_grid = QVBoxLayout()
        chips_grid.setSpacing(6)

        if is_pc_src:
            phone_chips = [
                ("Downloads", "/sdcard/Download"),
                ("DCIM / Camera", "/sdcard/DCIM"),
                ("Pictures", "/sdcard/Pictures"),
                ("Movies", "/sdcard/Movies"),
                ("Music", "/sdcard/Music"),
            ]
            row1 = QHBoxLayout()
            row1.setSpacing(6)
            row2 = QHBoxLayout()
            row2.setSpacing(6)
            for i, (name, path) in enumerate(phone_chips):
                btn = QPushButton(name)
                btn.setObjectName("DestQuickChip")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda _, p=path: self.set_dest_quick_chip(p))
                self.chip_buttons.append((btn, path))
                if i < 2:
                    row1.addWidget(btn)
                else:
                    row2.addWidget(btn)
            chips_grid.addLayout(row1)
            chips_grid.addLayout(row2)
        else:
            home = os.path.expanduser('~')
            pc_chips = [
                ("Downloads", os.path.join(home, 'Downloads')),
                ("Desktop", os.path.join(home, 'Desktop')),
                ("Pictures", os.path.join(home, 'Pictures')),
                ("Videos", os.path.join(home, 'Videos')),
                ("Warp Backup", self.config.get("backup_destination", os.path.join(home, 'Downloads', 'WarpTransferBackup'))),
            ]
            row1 = QHBoxLayout()
            row1.setSpacing(6)
            row2 = QHBoxLayout()
            row2.setSpacing(6)
            for i, (name, path) in enumerate(pc_chips):
                btn = QPushButton(name)
                btn.setObjectName("DestQuickChip")
                btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda _, p=path: self.set_dest_quick_chip(p))
                self.chip_buttons.append((btn, path))
                if i < 2:
                    row1.addWidget(btn)
                else:
                    row2.addWidget(btn)
            chips_grid.addLayout(row1)
            chips_grid.addLayout(row2)

        chips_section.addLayout(chips_grid)
        right_layout.addLayout(chips_section)
        right_layout.addStretch()
        split_layout.addWidget(right_col, 1)

        layout.addLayout(split_layout, 1)

        # 3. Bottom Action & Mode Bar
        bottom_bar = QHBoxLayout()
        bottom_bar.setSpacing(12)

        # Mode Segment Switcher
        mode_box = QHBoxLayout()
        mode_box.setSpacing(6)

        self.copy_mode_btn = QPushButton("📋 Copy", self)
        self.copy_mode_btn.setObjectName("ModeSegmentBtn")
        self.copy_mode_btn.setCheckable(True)
        self.copy_mode_btn.setChecked(self.transfer_mode == "copy")
        self.copy_mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_mode_btn.clicked.connect(lambda: self.set_transfer_mode("copy"))
        mode_box.addWidget(self.copy_mode_btn)

        self.move_mode_btn = QPushButton("✂️ Move", self)
        self.move_mode_btn.setObjectName("ModeSegmentBtn")
        self.move_mode_btn.setCheckable(True)
        self.move_mode_btn.setChecked(self.transfer_mode == "move")
        self.move_mode_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.move_mode_btn.clicked.connect(lambda: self.set_transfer_mode("move"))
        mode_box.addWidget(self.move_mode_btn)

        self.move_warning_label = QLabel("Deletes source files after verify")
        self.move_warning_label.setObjectName("DangerStatusLabel")
        self.move_warning_label.setVisible(self.transfer_mode == "move")
        mode_box.addWidget(self.move_warning_label)
        bottom_bar.addLayout(mode_box)

        bottom_bar.addStretch()

        # Start Transfer Button
        self.start_transfer_btn = QPushButton("Start Transfer ➔", self)
        self.start_transfer_btn.setObjectName("PrimaryButton")
        self.start_transfer_btn.setFixedHeight(38)
        self.start_transfer_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_transfer_btn.clicked.connect(self.execute_staged_transfer)
        bottom_bar.addWidget(self.start_transfer_btn)

        layout.addLayout(bottom_bar)

        add_shadow(left_col, blur=18, y_offset=4, alpha=40)
        add_shadow(right_col, blur=18, y_offset=4, alpha=40)

        self.stacked_pages.addWidget(self.dashboard_page_widget)
        self._fade_transition(self.dashboard_page_widget)
        self._tag_theme(self.dashboard_page_widget)
        
        self.refresh_workspace_ui()
        self.refresh_destination_ui()

    def execute_staged_transfer(self):
        if not self.staged_items:
            return
        if self.active_coordinator:
            return
        src_paths = [item["path"] for item in self.staged_items]
        self.start_transfer_ui(
            self.transfer_direction,
            self.transfer_mode,
            src_paths,
            self.current_dest_path
        )

    # --- 4-Stage Stepper Progress Screen ---

    def _build_stepper_node(self, step_num: int, title_text: str, parent: QWidget) -> tuple[QWidget, QLabel, QLabel]:
        node = QWidget(parent)
        layout = QVBoxLayout(node)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(3)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        badge = QLabel(str(step_num), node)
        badge.setObjectName("StepBadge")
        badge.setProperty("stepState", "pending")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(badge, 0, Qt.AlignmentFlag.AlignCenter)

        label = QLabel(title_text, node)
        label.setObjectName("StepLabel")
        label.setProperty("stepState", "pending")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, 0, Qt.AlignmentFlag.AlignCenter)

        return node, badge, label

    def start_transfer_ui(self, direction, op_type, src_paths, dest_path, extensions=None):
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(36, 24, 36, 24)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setObjectName("CardContainer")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title_text = "Moving Files..." if op_type == "move" else "Transferring Files..."
        title = QLabel(title_text, card)
        title.setObjectName("HeaderLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        route_label = QLabel(self._format_transfer_route(direction, src_paths, dest_path), card)
        route_label.setObjectName("PathLabel")
        route_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        route_label.setWordWrap(True)
        layout.addWidget(route_label)

        # 4-Stage Pipeline Stepper
        stepper_box = QWidget(card)
        stepper_box.setObjectName("StepperContainer")
        stepper_layout = QHBoxLayout(stepper_box)
        stepper_layout.setContentsMargins(12, 10, 12, 10)
        stepper_layout.setSpacing(6)

        self.stepper_nodes = {}
        steps_info = [
            ("indexing", 1, "Indexing"),
            ("setup", 2, "Channel Setup"),
            ("streaming", 3, "Transferring"),
            ("verifying", 4, "Verification"),
        ]

        for i, (key, num, stitle) in enumerate(steps_info):
            node, badge, lbl = self._build_stepper_node(num, stitle, stepper_box)
            self.stepper_nodes[key] = {"badge": badge, "label": lbl, "num": num}
            stepper_layout.addWidget(node)
            if i < len(steps_info) - 1:
                conn = QWidget(stepper_box)
                conn.setObjectName("StepConnector")
                conn.setFixedHeight(2)
                stepper_layout.addWidget(conn, 1)

        layout.addWidget(stepper_box)
        
        self.transfer_file_label = QLabel("Initializing engine...", card)
        self.transfer_file_label.setObjectName("TransferFileLabel")
        self.transfer_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.transfer_file_label)
        
        self.transfer_bar = QProgressBar(card)
        self.transfer_bar.setFixedHeight(12)
        self.transfer_bar.setValue(0)
        layout.addWidget(self.transfer_bar)
        
        # Detail telemetry card
        detail_card = QWidget()
        detail_card.setObjectName("InnerCard")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(14, 10, 14, 10)
        self.transfer_details = QLabel("Preparing worker channels...", detail_card)
        self.transfer_details.setObjectName("TransferDetailLabel")
        self.transfer_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.transfer_details.setWordWrap(True)
        detail_layout.addWidget(self.transfer_details)
        layout.addWidget(detail_card)

        # Controls Row
        controls_row = QHBoxLayout()
        controls_row.setSpacing(10)

        self.transfer_pause_btn = QPushButton("Pause", card)
        self.transfer_pause_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("pause", self.is_dark_mode), QSize(13, 13))))
        self.transfer_pause_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.transfer_pause_btn.clicked.connect(self.toggle_pause_transfer)
        controls_row.addWidget(self.transfer_pause_btn)

        self.transfer_cancel_btn = QPushButton("Cancel Transfer", card)
        self.transfer_cancel_btn.setObjectName("DangerButton")
        self.transfer_cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.transfer_cancel_btn.clicked.connect(self.cancel_active_transfer)
        controls_row.addWidget(self.transfer_cancel_btn)

        layout.addLayout(controls_row)

        outer_layout.addWidget(card)
        add_shadow(card, blur=28, y_offset=8, alpha=70)
        
        idx = self.stacked_pages.addWidget(page)
        self._fade_transition(idx)
        self._tag_theme(page)
        
        # Stop background connection checks during active transfer
        self.check_timer.stop()
        self.history_btn.setEnabled(False)
        self.settings_btn.setEnabled(False)
        self.is_paused = False
        self._transfer_start_time = time.time()
        self._transfer_context = {
            "direction": direction,
            "operation_type": op_type,
            "device_name": self.adb_manager.current_device,
        }
        
        # Start core coordinator engine
        self.active_coordinator = TransferCoordinator(
            self.adb_manager, direction, op_type, src_paths, dest_path,
            conflict_mode=self.config.get("conflict_mode", "ask"),
            throttle_kbps=self.config.get("throttle_kbps", 0),
            extensions=extensions,
        )
        self.active_coordinator.stage_changed.connect(self.on_transfer_stage_changed)
        self.active_coordinator.progress_updated.connect(self.update_transfer_progress)
        self.active_coordinator.transfer_finished.connect(self.on_transfer_finished)
        self.active_coordinator.conflicts_found.connect(self.handle_conflicts_found)
        self.active_coordinator.paused_changed.connect(self.on_paused_changed)
        self.active_coordinator.start()

    def on_transfer_stage_changed(self, stage_id: str, stage_desc: str):
        self.transfer_file_label.setText(stage_desc)
        stage_order = ["indexing", "setup", "streaming", "verifying"]
        current_idx = stage_order.index(stage_id) if stage_id in stage_order else 0

        for idx, key in enumerate(stage_order):
            if key not in self.stepper_nodes:
                continue
            badge = self.stepper_nodes[key]["badge"]
            label = self.stepper_nodes[key]["label"]
            num = self.stepper_nodes[key]["num"]

            if idx < current_idx:
                badge.setProperty("stepState", "done")
                badge.setText("✓")
                label.setProperty("stepState", "done")
            elif idx == current_idx:
                badge.setProperty("stepState", "active")
                badge.setText(str(num))
                label.setProperty("stepState", "active")
            else:
                badge.setProperty("stepState", "pending")
                badge.setText(str(num))
                label.setProperty("stepState", "pending")

            badge.style().unpolish(badge)
            badge.style().polish(badge)
            label.style().unpolish(label)
            label.style().polish(label)

    @staticmethod
    def _format_transfer_route(direction, src_paths, dest_path) -> str:
        if len(src_paths) == 1:
            src_display = os.path.basename(src_paths[0].rstrip("/\\")) or src_paths[0]
        else:
            src_display = f"{len(src_paths)} selected item(s)"

        dest_display = dest_path
        if len(dest_display) > 42:
            dest_display = dest_display[:20] + "..." + dest_display[-18:]

        dir_str = "Phone ➔ PC" if direction == "phone_to_pc" else "PC ➔ Phone"
        return f"{src_display}  •  {dir_str}\nTo: {dest_display}"

    def handle_conflicts_found(self, count):
        mode = ConflictDialog.ask(count, self.is_dark_mode, self)
        if self.active_coordinator:
            self.active_coordinator.resolve_conflict(mode)

    def toggle_pause_transfer(self):
        if not self.active_coordinator:
            return
        if self.is_paused:
            self.active_coordinator.resume()
        else:
            self.active_coordinator.pause()

    def on_paused_changed(self, paused):
        self.is_paused = paused
        if paused:
            self.transfer_pause_btn.setText("Resume")
            self.transfer_pause_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("play", self.is_dark_mode), QSize(13, 13))))
            self.transfer_details.setText("Paused — tap Resume to continue.")
        else:
            self.transfer_pause_btn.setText("Pause")
            self.transfer_pause_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("pause", self.is_dark_mode), QSize(13, 13))))

    @staticmethod
    def _format_speed(speed_mbs: float) -> str:
        if speed_mbs <= 0:
            return "-- MB/s"
        if speed_mbs < 1:
            return f"{speed_mbs * 1024:.0f} KB/s"
        if speed_mbs >= 1024:
            return f"{speed_mbs / 1024:.2f} GB/s"
        return f"{speed_mbs:.1f} MB/s"

    @staticmethod
    def _format_eta(eta_seconds: float) -> str:
        if eta_seconds <= 0:
            return "calculating..."
        eta_seconds = int(round(eta_seconds))
        if eta_seconds < 60:
            return f"{eta_seconds}s left"
        minutes, seconds = divmod(eta_seconds, 60)
        if minutes < 60:
            return f"{minutes}m {seconds:02d}s left"
        hours, minutes = divmod(minutes, 60)
        return f"{hours}h {minutes:02d}m left"

    def update_transfer_progress(self, current_files, total_files, percent, speed_mbs, eta_seconds, current_file):
        if self.is_paused:
            return
        if len(current_file) > 50:
            current_file = current_file[:22] + "..." + current_file[-25:]
        self.transfer_file_label.setText(current_file)
        self.transfer_bar.setValue(int(percent))
        
        if total_files > 0:
            self.transfer_details.setText(
                f"{current_files} of {total_files} files ({percent:.1f}%)  •  "
                f"{self._format_speed(speed_mbs)}  •  {self._format_eta(eta_seconds)}"
            )
        else:
            self.transfer_details.setText(current_file)

    def cancel_active_transfer(self):
        if self.active_coordinator:
            self.active_cancel_btn_disabled()
            self.active_coordinator.cancel()

    def active_cancel_btn_disabled(self):
        self.transfer_cancel_btn.setEnabled(False)
        self.transfer_cancel_btn.setText("Cancelling...")
        self.transfer_pause_btn.setEnabled(False)

    def on_transfer_finished(self, success, message):
        duration = time.time() - self._transfer_start_time if self._transfer_start_time else 0
        coordinator = self.active_coordinator
        if coordinator is not None:
            history_manager.add_entry(
                direction=self._transfer_context.get("direction", ""),
                operation_type=self._transfer_context.get("operation_type", ""),
                file_count=coordinator.copied_files,
                total_bytes=coordinator.copied_bytes,
                success=success,
                message=message,
                duration_seconds=duration,
                device_name=self._transfer_context.get("device_name", ""),
            )
        self.active_coordinator = None
        self.history_btn.setEnabled(True)
        self.settings_btn.setEnabled(True)
        self.staged_items.clear()
        
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(40, 40, 40, 40)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setObjectName("CardContainer")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_badge = make_icon_badge("check" if success else "alert", self.is_dark_mode, size=72, icon_size=40)
        layout.addWidget(icon_badge, 0, Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Transfer Succeeded!" if success else "Transfer Failed", card)
        title.setObjectName("HeaderLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        desc = QLabel(message, card)
        desc.setObjectName("SubHeaderLabel")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        done_btn = QPushButton("Done", card)
        done_btn.setObjectName("PrimaryButton")
        done_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        done_btn.clicked.connect(self.return_to_dashboard)
        layout.addWidget(done_btn)

        outer_layout.addWidget(card)
        add_shadow(card, blur=28, y_offset=8, alpha=70)
        
        idx = self.stacked_pages.addWidget(page)
        self._fade_transition(idx)
        self._tag_theme(page)

    def return_to_dashboard(self):
        if self.active_coordinator is not None:
            return
        self.check_timer.start(1500)
        self.show_onboarding_or_dashboard()

    def get_truncated_dest_path(self) -> str:
        path = self.config["backup_destination"]
        if len(path) > 42:
            return path[:20] + "..." + path[-20:]
        return path

    def change_backup_destination(self):
        new_dir = QFileDialog.getExistingDirectory(
            self, 
            "Select Backup Destination Folder", 
            self.config["backup_destination"]
        )
        if new_dir:
            self.config["backup_destination"] = os.path.abspath(new_dir)
            self.save_config()
            if hasattr(self, "settings_dest_label"):
                self.settings_dest_label.setText(self.get_truncated_dest_path())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
