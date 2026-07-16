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
from copy_move_dialog import CopyMoveDialog
from ui_transitions import fade_to_page
from theme_utils import tag_theme_recursive

# Raw SVG Icons (Lucide style)
SVG_PHONE = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/><line x1="12" x2="12.01" y1="18" y2="18"/></svg>'
SVG_FOLDER = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 20h16a2 2 0 0 0 2-2V8a2 2 0 0 0-2-2h-7.93a2 2 0 0 1-1.66-.9l-.82-1.2A2 2 0 0 0 7.93 3H4a2 2 0 0 0-2 2v13a2 2 0 0 0 2 2Z"/></svg>'
SVG_ARROW_LEFT_RIGHT = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 3 4 4-4 4"/><path d="M20 7H4"/><path d="m8 21-4-4 4-4"/><path d="M4 17h16"/></svg>'
SVG_CHECK = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#34C759" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/></svg>'
SVG_ALERT = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#FF453A" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>'
SVG_DOWNLOAD = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" x2="12" y1="15" y2="3"/></svg>'
SVG_CLOSE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" x2="6" y1="6" y2="18"/><line x1="6" x2="18" y1="6" y2="18"/></svg>'
SVG_MINIMIZE = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" x2="19" y1="12" y2="12"/></svg>'
SVG_ZAP = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>'
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

PHOTO_EXTENSIONS = ["jpg", "jpeg", "png", "webp", "heic", "gif", "bmp"]
VIDEO_EXTENSIONS = ["mp4", "mov", "mkv", "3gp", "avi", "webm"]


def get_svg_content(icon_name, is_dark) -> str:
    accent = "#D4AF37" if is_dark else "#B8860B"
    text_color = "#F2F2F7" if is_dark else "#1C1C1E"
    muted = "#9C9CA3" if is_dark else "#8E8E93"
    
    if icon_name == "phone":
        return SVG_PHONE.format(color=accent)
    elif icon_name == "folder":
        return SVG_FOLDER.format(color=accent)
    elif icon_name == "arrow_left_right":
        return SVG_ARROW_LEFT_RIGHT.format(color=text_color)
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DropZone")
        self.setAcceptDrops(True)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 26, 20, 26)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(10)
        
        self.icon_badge_container = QWidget()
        badge_wrap_layout = QVBoxLayout(self.icon_badge_container)
        badge_wrap_layout.setContentsMargins(0, 0, 0, 8)
        badge_wrap_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_wrap_layout.addWidget(self.icon_label)
        layout.addWidget(self.icon_badge_container)
        
        self.text_label = QLabel("Drag & Drop Files Here\nto transfer directly to your phone's storage")
        self.text_label.setObjectName("DragDropTitleLabel")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)
        
        self.subtext = QLabel("Supports files & entire directories")
        self.subtext.setObjectName("DragDropSubtextLabel")
        self.subtext.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.subtext)

    def update_theme(self, is_dark):
        svg_content = get_svg_content("arrow_left_right", is_dark)
        self.icon_label.setPixmap(get_svg_pixmap(svg_content, QSize(32, 32)))

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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Pre-initialize page references to prevent AttributeError during early timer checks
        self.onboarding_page_widget = None
        self.dashboard_page_widget = None
        self.history_page_widget = None
        self.settings_page_widget = None
        
        self.setWindowTitle("Warp Transfer")
        # 760x600 is the visible card size; +48 in each dimension (24px on
        # every side) is transparent padding for main_container's ambient
        # drop shadow (blur=40 in apply_theme()) to bleed into. Previously
        # main_container filled the window with zero margin, so the shadow's
        # blur radius extended past the window's actual pixel bounds --
        # Qt then tried to composite a paint region larger than the native
        # HWND's layered-window buffer, which Windows rejected with
        # "UpdateLayeredWindowIndirect failed ... (The parameter is
        # incorrect.)" on every apply_theme() call (visible in the console
        # on launch and on every theme toggle -- see Session N+9 screenshot).
        self.setFixedSize(760 + 48, 600 + 48)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Load local configuration
        self.config_path = os.path.join(os.path.expanduser('~'), 'warp_transfer_config.json')
        self.load_config()
        
        self.is_dark_mode = self.config.get("theme", "light") == "dark"
        
        self.adb_manager = AdbManager()
        self.drag_position = QPoint()
        self.active_coordinator = None
        self.is_paused = False
        self._transfer_start_time = 0
        self._transfer_context = {}  # direction/op_type for history logging
        # Phase 2 (motion): tracks whether a page cross-fade is still
        # animating, and holds refs to in-flight animations so PyQt doesn't
        # garbage-collect them mid-flight (see ui_transitions.fade_to_page).
        self._transition_in_progress = False
        self._page_fade_anim = None
        self._theme_fade_anim = None
        
        self.init_ui()
        self.apply_theme()
        
        # Connection status check timer
        self.check_timer = QTimer(self)
        self.check_timer.timeout.connect(self.check_device_connection)
        
        # Check ADB install first
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
            "theme": "light",  # Default to light mode
            "conflict_mode": "ask",  # ask | skip | overwrite | rename
            "throttle_kbps": 0,  # 0 = unlimited
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
        """Phase 4 (localsend_parity_plan.md): persist a successfully-connected
        device into config["known_devices"] = {device_id: friendly_name}, so
        OnboardingWizard can show the lightweight reconnect view instead of
        the full first-time setup wizard next time this exact device shows up.
        NOTE: this was previously read at one call site but never written
        anywhere -- known_devices stayed permanently empty, so the reconnect
        view could never actually trigger. Only writes+saves when the value
        genuinely changed, since this is called from the 1.5s poll timer and
        a disk write on every single tick while already connected would be
        wasteful."""
        if not device_id:
            return
        known = self.config.setdefault("known_devices", {})
        if known.get(device_id) != friendly_name:
            known[device_id] = friendly_name
            self.save_config()

    def init_ui(self):
        # Outer transparent wrapper providing the padding main_container's
        # shadow needs (see setFixedSize's comment in __init__ for why this
        # exists). main_container itself keeps its own object name/QSS and
        # visible rounded-rect styling unchanged -- only WHERE it sits inside
        # the window changed, not what it looks like.
        outer_wrapper = QWidget(self)
        self.setCentralWidget(outer_wrapper)
        outer_wrapper_layout = QVBoxLayout(outer_wrapper)
        outer_wrapper_layout.setContentsMargins(24, 24, 24, 24)
        outer_wrapper_layout.setSpacing(0)

        # Window Shadow & Rounded Outline Container
        self.main_container = QWidget(outer_wrapper)
        self.main_container.setObjectName("MainWindowContainer")
        outer_wrapper_layout.addWidget(self.main_container)
        
        main_layout = QVBoxLayout(self.main_container)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header/Titlebar (Frameless movement handler)
        self.title_bar = QWidget(self)
        self.title_bar.setObjectName("TitleBar")
        self.title_bar.setFixedHeight(52)
        
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(18, 0, 12, 0)
        title_layout.setSpacing(10)
        
        # Logo badge (accent-tinted rounded container around the app icon)
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

        # History button
        self.history_btn = QPushButton()
        self.history_btn.setObjectName("TitleBarButton")
        self.history_btn.setFixedSize(30, 30)
        self.history_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_btn.setToolTip("Transfer history")
        self.history_btn.clicked.connect(self.show_history_page)
        title_layout.addWidget(self.history_btn)

        # Settings button
        self.settings_btn = QPushButton()
        self.settings_btn.setObjectName("TitleBarButton")
        self.settings_btn.setFixedSize(30, 30)
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.clicked.connect(self.show_settings_page)
        title_layout.addWidget(self.settings_btn)
        
        # Theme toggle button
        self.theme_btn = QPushButton()
        self.theme_btn.setObjectName("TitleBarButton")
        self.theme_btn.setFixedSize(30, 30)
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setToolTip("Toggle theme")
        self.theme_btn.clicked.connect(self.toggle_theme)
        title_layout.addWidget(self.theme_btn)
        
        # Minimize button
        self.min_btn = QPushButton()
        self.min_btn.setObjectName("TitleBarButton")
        self.min_btn.setFixedSize(30, 30)
        self.min_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.min_btn.setToolTip("Minimize")
        self.min_btn.clicked.connect(self.showMinimized)
        title_layout.addWidget(self.min_btn)
        
        # Close button
        self.close_btn = QPushButton()
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip("Close")
        self.close_btn.clicked.connect(self.close_app)
        title_layout.addWidget(self.close_btn)
        
        main_layout.addWidget(self.title_bar)
        
        # Content Pages Stack
        self.stacked_pages = QStackedWidget(self)
        main_layout.addWidget(self.stacked_pages)
        
        # Mouse drag events on titlebar for frameless movement
        self.title_bar.mousePressEvent = self.title_bar_press
        self.title_bar.mouseMoveEvent = self.title_bar_move

    def apply_theme(self):
        # Phase 3 rewrite: APP_STYLE (app_style.py) is ONE merged stylesheet
        # whose selectors are gated on a `theme="dark"/"light"` dynamic QSS
        # property, loaded into the QApplication exactly ONCE (guarded by
        # _warp_stylesheet_loaded below). Toggling theme no longer calls
        # setStyleSheet() again -- that used to force Qt to fully re-parse
        # and re-cascade the entire stylesheet string across the whole
        # widget tree on every single click (see dev_notes.md Session N+2/
        # N+3 for the black-square-flash bug this caused). Now toggling just
        # flips the `theme` property + unpolish()/polish() via _tag_theme(),
        # which only re-matches selectors -- much cheaper.
        app = QApplication.instance()
        if app and not getattr(app, "_warp_stylesheet_loaded", False):
            app.setStyleSheet(APP_STYLE)
            app._warp_stylesheet_loaded = True

        self._tag_theme(self)

        # 2. Update Window Border Color based on theme
        bg_color = "#0C0C0E" if self.is_dark_mode else "#F2F2F7"
        border_color = "#1E1E24" if self.is_dark_mode else "#D1D1D6"
        self.main_container.setStyleSheet(f"""
            #MainWindowContainer {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 16px;
            }}
        """)
        
        # Soft ambient shadow around the whole frameless window for depth
        # against the desktop background.
        add_shadow(self.main_container, blur=40, y_offset=10, alpha=110)
        
        # 3. Render titlebar and toggle icons
        self.title_logo.setPixmap(get_svg_pixmap(get_svg_content("phone", self.is_dark_mode), QSize(18, 18)))
        
        # Icon pixmaps are swapped per-theme here (get_svg_content bakes the
        # accent color into the SVG string, so no QSS property change alone
        # covers that) -- but the buttons' own background/border/hover/pressed
        # appearance is NOT set here anymore. It used to be: every one of
        # these 5 buttons got an instance-level setStyleSheet("background:
        # transparent; border: none; ...") call on every single toggle, even
        # though #TitleBarButton's QSS base rule (app_style.py) already
        # declares the identical unconditional background/border, and
        # #TitleBarButton[theme="..."]:hover/:pressed already define the
        # correct per-theme hover colors. Mixing an instance-level stylesheet
        # with the property-based global QSS on the same widgets, re-applied
        # every toggle, is what caused settings_btn/theme_btn specifically to
        # sometimes render the WRONG theme's hover/pressed color as a
        # persistent solid box (confirmed via screenshot: a white box on
        # settings/theme in dark mode, a black box on the same two in light
        # mode -- exactly the opposite theme's #TitleBarButton hover color in
        # both cases). Deleting the redundant instance stylesheets and
        # letting _tag_theme()'s property+polish mechanism own these buttons
        # completely, same as every other themed widget in the app, removes
        # the conflict at the source instead of chasing the exact Qt caching
        # quirk that triggered it.
        self.theme_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("sun" if self.is_dark_mode else "moon", self.is_dark_mode), QSize(14, 14))))

        self.history_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("history", self.is_dark_mode), QSize(15, 15))))

        self.settings_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("settings", self.is_dark_mode), QSize(15, 15))))
        
        self.min_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("minimize", self.is_dark_mode), QSize(14, 14))))
        
        self.close_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("close", self.is_dark_mode), QSize(14, 14))))
        
        # 4. Propagate theme updates to child elements if active
        if self.dashboard_page_widget:
            self.drop_zone.update_theme(self.is_dark_mode)
            self.device_icon_badge_refresh()

        # Settings/History pages are rebuilt fresh each time they're shown,
        # so no live-refresh needed for them here.

    def _tag_theme(self, widget):
        """Recursively set the `theme` dynamic property (+ unpolish/polish)
        on `widget` and every descendant. Qt QSS attribute selectors like
        [theme="dark"] are NOT inherited from an ancestor -- each widget
        needs the property set on itself for its own rules to match. Call
        this from apply_theme() on toggle (covers self + whatever's already
        built), AND on any newly created widget subtree (new pages) so it
        picks up the CURRENT theme immediately instead of waiting for the
        next toggle to get tagged.

        FIXED (was a known gap through Session N+9): ConflictDialog and
        DevicePickerDialog previously built+exec()'d themselves in one
        static ask(...) call, so MainWindow never had a handle to tag them
        before they showed. Both dialogs now call the same
        theme_utils.tag_theme_recursive() this method delegates to,
        themselves, from their own __init__ -- see conflict_dialog.py /
        device_picker.py. WirelessConnectDialog was already covered, since
        MainWindow constructs it directly (see open_wireless_dialog).
        """
        # Delegates to the shared theme_utils.tag_theme_recursive() helper
        # (queue item #1 fix) -- previously this loop lived only here, which
        # is exactly why ConflictDialog/DevicePickerDialog never got tagged:
        # there was nothing for them to call. Extracting it means both
        # dialogs now get the identical, already-proven-correct behavior
        # (including the setUpdatesEnabled freeze from Session N+8) instead
        # of a duplicated or simplified copy.
        tag_theme_recursive(widget, self.is_dark_mode)

    def _fade_transition(self, target):
        """Cross-fade `stacked_pages` to `target` (page index or widget) via
        the shared `fade_to_page` helper (ui_transitions.py) instead of a
        hard setCurrentIndex()/setCurrentWidget() cut -- see
        localsend_parity_plan.md Phase 2. Sets `_transition_in_progress` for
        the fade's duration so check_device_connection's 1.5s poll doesn't
        stack a second automatic dashboard<->onboarding transition on top of
        one that's still animating. Keeps the returned animation on
        `self._page_fade_anim` so it isn't garbage-collected mid-flight."""
        self._transition_in_progress = True

        def _done():
            self._transition_in_progress = False

        self._page_fade_anim = fade_to_page(self.stacked_pages, target, on_finished=_done)

    def device_icon_badge_refresh(self):
        # Rebuild the phone icon inside the connected-device badge for the
        # current theme's accent colour.
        if hasattr(self, "device_icon"):
            self.device_icon.setPixmap(get_svg_pixmap(get_svg_content("phone", self.is_dark_mode), QSize(20, 20)))

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        # Repaint first, persist after. apply_theme() is now cheap (Phase 3:
        # property flip + unpolish/polish instead of a full-app
        # setStyleSheet() re-parse), but there's no reason to make the
        # config disk write block the repaint either way, so it still stays
        # deferred via QTimer.singleShot(0, ...) to the next event-loop
        # iteration.
        self.apply_theme()

        # Phase 2 (motion): a brief cross-fade to smooth over any remaining
        # one-frame pop from the property swap. Animates the whole window's
        # native windowOpacity rather than a per-widget QGraphicsOpacityEffect
        # -- main_container already carries a QGraphicsDropShadowEffect
        # (re-applied by apply_theme()'s add_shadow() call on every toggle),
        # and a QWidget can only hold one graphics effect at a time, so an
        # opacity effect on main_container would fight the shadow instead of
        # coexisting with it. windowOpacity sidesteps that entirely.
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

    # Frameless window dragging methods
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
        dlg = WirelessConnectDialog(self.adb_manager, self)
        self._tag_theme(dlg)
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

    # Create & display Dashboard view
    def show_dashboard_page(self, device_name):
        # Drop any previous dashboard widget before building a fresh one.
        # This method can be re-entered automatically (via check_device_connection's
        # 1.5s poll) on flaky USB/wireless connections, so without this guard a
        # long, unstable session would silently accumulate one orphaned
        # QWidget tree per reconnect for as long as the app stays open.
        if self.dashboard_page_widget is not None:
            self.stacked_pages.removeWidget(self.dashboard_page_widget)
            self.dashboard_page_widget.deleteLater()
            self.dashboard_page_widget = None

        self.dashboard_page_widget = QWidget()
        layout = QVBoxLayout(self.dashboard_page_widget)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(14)
        
        # Connected Device Header Bar
        header = QWidget()
        header.setObjectName("InnerCard")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 12, 15, 12)
        header_layout.setSpacing(12)
        
        device_icon_badge = QWidget()
        device_icon_badge.setObjectName("IconBadge")
        device_icon_badge.setFixedSize(38, 38)
        dib_layout = QVBoxLayout(device_icon_badge)
        dib_layout.setContentsMargins(0, 0, 0, 0)
        dib_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.device_icon = QLabel()
        self.device_icon.setPixmap(get_svg_pixmap(get_svg_content("phone", self.is_dark_mode), QSize(20, 20)))
        dib_layout.addWidget(self.device_icon)
        header_layout.addWidget(device_icon_badge)
        
        device_info = QVBoxLayout()
        device_info.setSpacing(2)
        device_title = QLabel(device_name)
        device_title.setObjectName("DeviceTitleLabel")
        device_status = QLabel("Connected via USB Debugging (Max Speed)")
        device_status.setObjectName("SuccessStatusLabel")
        device_info.addWidget(device_title)
        device_info.addWidget(device_status)
        header_layout.addLayout(device_info)
        header_layout.addStretch()
        
        layout.addWidget(header)
        
        # Grid of Quick Action Buttons -- main backups
        quick_grid = QHBoxLayout()
        quick_grid.setSpacing(15)
        
        media_btn = self._build_quick_action(
            "zap", "Quick Media Backup", "Backup DCIM, Camera, & Photos to your PC",
            self.trigger_media_backup
        )
        quick_grid.addWidget(media_btn)
        
        android_btn = self._build_quick_action(
            "folder", "Android Folder Backup", "Backup entire /sdcard/Android folder using parallel streams",
            self.trigger_android_backup
        )
        quick_grid.addWidget(android_btn)
        
        layout.addLayout(quick_grid)

        # Second row: filtered quick backups (Photos Only / Videos Only)
        filter_grid = QHBoxLayout()
        filter_grid.setSpacing(15)

        photos_btn = self._build_quick_action(
            "image", "Photos Only", "Backup just image files from DCIM & Pictures",
            self.trigger_photos_backup
        )
        filter_grid.addWidget(photos_btn)

        videos_btn = self._build_quick_action(
            "video", "Videos Only", "Backup just video files from DCIM & Movies",
            self.trigger_videos_backup
        )
        filter_grid.addWidget(videos_btn)

        layout.addLayout(filter_grid)
        
        # Drag & Drop Zone
        self.drop_zone = DragDropZone(self)
        self.drop_zone.update_theme(self.is_dark_mode)
        self.drop_zone.files_dropped.connect(self.handle_drag_dropped_files)
        layout.addWidget(self.drop_zone)
        
        # Footer Action Row (destination glance + custom transfer)
        footer = QHBoxLayout()
        
        dest_layout = QVBoxLayout()
        dest_layout.setSpacing(2)
        dest_header = QLabel("Backup Destination:")
        dest_header.setObjectName("DestHeaderLabel")
        self.dest_label = QLabel(self.get_truncated_dest_path())
        self.dest_label.setObjectName("PathLabel")
        dest_layout.addWidget(dest_header)
        dest_layout.addWidget(self.dest_label)
        footer.addLayout(dest_layout)
        
        footer.addStretch()

        # Explicit PC -> Phone entry point (previously only reachable via
        # implicit drag-and-drop, and only ever as a Copy). Placed next to
        # Pull Custom Files so both transfer directions are equally
        # discoverable from the same footer row.
        push_custom_btn = QPushButton("Push Files to Phone", self)
        push_custom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        push_custom_btn.clicked.connect(self.trigger_custom_push)
        footer.addWidget(push_custom_btn)

        pull_custom_btn = QPushButton("Pull Custom Files", self)
        pull_custom_btn.setObjectName("PrimaryButton")
        pull_custom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pull_custom_btn.clicked.connect(self.trigger_custom_pull)
        footer.addWidget(pull_custom_btn)
        
        layout.addLayout(footer)
        
        # Subtle elevation for the header card and drop zone.
        # Quick-action tiles now manage their own hover-responsive shadow
        # via the QuickActionButton class, so they're not set here.
        add_shadow(header, blur=18, y_offset=3, alpha=60)
        add_shadow(self.drop_zone, blur=20, y_offset=4, alpha=40)
        
        self.stacked_pages.addWidget(self.dashboard_page_widget)
        self._fade_transition(self.dashboard_page_widget)
        self._tag_theme(self.dashboard_page_widget)

    def _build_quick_action(self, icon_name, title_text, desc_text, on_click) -> QWidget:
        btn = QuickActionButton()
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.clicked.connect(on_click)
        outer = QVBoxLayout(btn)
        # #QuickActionButton's QSS rule declares `padding: 16px`, but that's
        # only ever honored by Qt for a QPushButton's own built-in text/icon
        # label rendering -- it is NOT applied to a manually-set child layout
        # like this one. With margins at 0 (the old value), the badge/title/
        # desc sat flush against the tile's rounded-corner edges instead of
        # getting the intended breathing room, which is what read as
        # "unpolished" on real-device screenshots. Setting the layout's own
        # margins to match the QSS intent directly, since that's the only
        # margin Qt will actually respect here.
        outer.setContentsMargins(16, 16, 16, 16)
        outer.setSpacing(10)
        badge = make_icon_badge(icon_name, self.is_dark_mode, size=36, icon_size=18)
        outer.addWidget(badge, 0, Qt.AlignmentFlag.AlignLeft)
        title = QLabel(title_text, btn)
        title.setObjectName("QuickActionButtonTitle")
        desc = QLabel(desc_text, btn)
        desc.setObjectName("QuickActionButtonDesc")
        desc.setWordWrap(True)
        outer.addWidget(title)
        outer.addWidget(desc)
        return btn

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
            if hasattr(self, "dest_label"):
                self.dest_label.setText(self.get_truncated_dest_path())
            if hasattr(self, "settings_dest_label"):
                self.settings_dest_label.setText(self.get_truncated_dest_path())

    @staticmethod
    def _format_transfer_route(direction, src_paths, dest_path) -> str:
        """One-line 'what's actually moving where' summary for the top of
        the progress page. Kept short/truncated since long absolute paths
        (especially Android ones) blow past the card's width easily."""
        if len(src_paths) == 1:
            src_display = os.path.basename(src_paths[0].rstrip("/\\")) or src_paths[0]
        else:
            src_display = f"{len(src_paths)} selected items"

        dest_display = dest_path
        if len(dest_display) > 44:
            dest_display = dest_display[:20] + "..." + dest_display[-20:]

        if direction == "phone_to_pc":
            return f"{src_display}  \u2022  Phone \u2192 PC\nTo: {dest_display}"
        return f"{src_display}  \u2022  PC \u2192 Phone\nTo: {dest_display}"

    # Trigger Transfers
    def start_transfer_ui(self, direction, op_type, src_paths, dest_path, extensions=None):
        # Setup Progress Page
        page = QWidget()
        outer_layout = QVBoxLayout(page)
        outer_layout.setContentsMargins(40, 40, 40, 40)
        outer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card = QWidget()
        card.setObjectName("CardContainer")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 36, 40, 36)
        layout.setSpacing(18)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        title = QLabel("Copying Files...", card)
        title.setObjectName("HeaderLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # FIX (real-device report: "progress page doesn't show any info such
        # as where it's copying from to where and what folder"): previously
        # nothing on this page ever showed the actual source/destination --
        # just generic placeholder text ("Initializing engine...") that
        # never changed until the per-file/batch labels below started
        # updating. This route line stays fixed for the whole transfer.
        route_label = QLabel(self._format_transfer_route(direction, src_paths, dest_path), card)
        route_label.setObjectName("PathLabel")
        route_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        route_label.setWordWrap(True)
        layout.addWidget(route_label)
        
        self.transfer_file_label = QLabel("Initializing engine...", card)
        self.transfer_file_label.setObjectName("TransferFileLabel")
        self.transfer_file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.transfer_file_label)
        
        self.transfer_bar = QProgressBar(card)
        self.transfer_bar.setFixedHeight(12)
        self.transfer_bar.setValue(0)
        layout.addWidget(self.transfer_bar)
        
        # Detail row wrapped in its own inner card for visual separation
        detail_card = QWidget()
        detail_card.setObjectName("InnerCard")
        detail_layout = QVBoxLayout(detail_card)
        detail_layout.setContentsMargins(16, 12, 16, 12)
        self.transfer_details = QLabel("Preparing worker threads...", detail_card)
        self.transfer_details.setObjectName("TransferDetailLabel")
        self.transfer_details.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.transfer_details.setWordWrap(True)
        detail_layout.addWidget(self.transfer_details)
        layout.addWidget(detail_card)

        # Pause/Resume + Cancel row
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
        # Visually disable History/Settings while a transfer is running --
        # paired with the active_coordinator guards in show_settings_page/
        # show_history_page/return_to_dashboard, so it's obvious up front
        # these aren't available rather than silently doing nothing on click.
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
        self.active_coordinator.progress_updated.connect(self.update_transfer_progress)
        self.active_coordinator.transfer_finished.connect(self.on_transfer_finished)
        self.active_coordinator.conflicts_found.connect(self.handle_conflicts_found)
        self.active_coordinator.paused_changed.connect(self.on_paused_changed)
        self.active_coordinator.start()

    def handle_conflicts_found(self, count):
        """Slot for TransferCoordinator.conflicts_found. Runs on the GUI
        thread (Qt auto-connects cross-thread signals as queued), shows a
        blocking dialog, then unblocks the coordinator's worker thread via
        resolve_conflict()."""
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
            self.transfer_details.setText("Paused \u2014 tap Resume to continue.")
        else:
            self.transfer_pause_btn.setText("Pause")
            self.transfer_pause_btn.setIcon(QIcon(get_svg_pixmap(get_svg_content("pause", self.is_dark_mode), QSize(13, 13))))

    @staticmethod
    def _format_speed(speed_mbs: float) -> str:
        """Adaptive speed formatting: KB/s for slow transfers, GB/s once
        it's fast enough that MB/s stops being readable at a glance."""
        if speed_mbs <= 0:
            return "-- MB/s"
        if speed_mbs < 1:
            return f"{speed_mbs * 1024:.0f} KB/s"
        if speed_mbs >= 1024:
            return f"{speed_mbs / 1024:.2f} GB/s"
        return f"{speed_mbs:.1f} MB/s"

    @staticmethod
    def _format_eta(eta_seconds: float) -> str:
        """Human-readable remaining time, e.g. '2m 14s left'."""
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
        # Log to history before clearing context.
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
        
        # Display Status Result View
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
        # Defensive backstop: Settings/History can no longer be entered
        # while a transfer is active (see show_settings_page), so this
        # should never actually fire mid-transfer -- but if it somehow does,
        # don't resume polling or rebuild the dashboard out from under a
        # still-running TransferCoordinator (the original real-device bug).
        if self.active_coordinator is not None:
            return
        self.check_timer.start(1500)
        self.show_onboarding_or_dashboard()

    # Pre-packaged Backup Triggers
    def trigger_media_backup(self):
        dest = self.config["backup_destination"]
        src_paths = [
            "/sdcard/DCIM",
            "/sdcard/Pictures",
            "/sdcard/Movies"
        ]
        self.start_transfer_ui("phone_to_pc", "copy", src_paths, dest)

    def trigger_android_backup(self):
        dest = self.config["backup_destination"]
        src_paths = ["/sdcard/Android"]
        self.start_transfer_ui("phone_to_pc", "copy", src_paths, dest)

    def trigger_photos_backup(self):
        dest = self.config["backup_destination"]
        src_paths = ["/sdcard/DCIM", "/sdcard/Pictures"]
        self.start_transfer_ui("phone_to_pc", "copy", src_paths, dest, extensions=PHOTO_EXTENSIONS)

    def trigger_videos_backup(self):
        dest = self.config["backup_destination"]
        src_paths = ["/sdcard/DCIM", "/sdcard/Movies"]
        self.start_transfer_ui("phone_to_pc", "copy", src_paths, dest, extensions=VIDEO_EXTENSIONS)

    def trigger_custom_pull(self):
        # FIX (real-device report): this previously ignored its own button
        # label entirely and silently pulled a hardcoded /sdcard/Download
        # every time. Now genuinely lets the user browse the phone and pick
        # specific files/folders via PhoneBrowserDialog, then choose Copy vs
        # Move via CopyMoveDialog (Move was previously unreachable from any
        # UI path despite being fully implemented in TransferCoordinator).
        if self.active_coordinator:
            return
        selected = PhoneBrowserDialog.ask(self.adb_manager, self.is_dark_mode, self)
        if not selected:
            return
        mode = CopyMoveDialog.ask(len(selected), self.is_dark_mode, self)
        if not mode:
            return
        dest = self.config["backup_destination"]
        self.start_transfer_ui("phone_to_pc", mode, selected, dest)

    def trigger_custom_push(self):
        # FIX (real-device report: "where is the option to copy/move from PC
        # to phone?"): previously the only PC-to-phone path was implicit
        # drag-and-drop, always hardcoded to Copy. This is the explicit,
        # discoverable entry point, with the same Copy/Move choice as Pull
        # Custom Files. Destination stays /sdcard/Download to match what
        # drag-and-drop already does -- a phone-side destination *folder*
        # picker is a reasonable future addition but is a separate, bigger
        # piece of work than this bug-fix pass.
        if self.active_coordinator:
            return
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files to Push to Phone")
        if not files:
            return
        mode = CopyMoveDialog.ask(len(files), self.is_dark_mode, self)
        if not mode:
            return
        dest = "/sdcard/Download"
        self.start_transfer_ui("pc_to_phone", mode, files, dest)

    def handle_drag_dropped_files(self, paths):
        dest = "/sdcard/Download"
        self.start_transfer_ui("pc_to_phone", "copy", paths, dest)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())
