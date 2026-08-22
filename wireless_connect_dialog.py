# Wireless (Wi-Fi) ADB connection dialog for Warp Transfer.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QWidget, QTabWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from theme_utils import tag_theme_recursive


class WirelessConnectDialog(QDialog):
    def __init__(self, adb_manager, is_dark: bool = True, parent=None):
        super().__init__(parent)
        self.adb_manager = adb_manager
        self.is_dark = is_dark
        self.setWindowTitle("Connect Wirelessly")
        self.setModal(True)
        self.setFixedSize(480, 420)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        card = QWidget(self)
        card.setObjectName("CardContainer")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 24, 26, 22)
        layout.setSpacing(14)

        title = QLabel("Connect Over Wi-Fi")
        title.setObjectName("HeaderLabel")
        title.setStyleSheet("font-size: 18px;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._build_pair_tab(), "Pair New Device")
        tabs.addTab(self._build_reconnect_tab(), "Reconnect")
        layout.addWidget(tabs)

        # Dismissable Status Banner
        self.status_banner = QWidget(card)
        self.status_banner.setObjectName("StatusBannerContainer")
        status_banner_layout = QHBoxLayout(self.status_banner)
        status_banner_layout.setContentsMargins(12, 8, 8, 8)
        status_banner_layout.setSpacing(8)

        self.status_label = QLabel("", self.status_banner)
        self.status_label.setObjectName("StatusBannerNeutral")
        self.status_label.setWordWrap(True)
        status_banner_layout.addWidget(self.status_label, 1)

        self.status_dismiss_btn = QPushButton("✕", self.status_banner)
        self.status_dismiss_btn.setObjectName("StatusDismissButton")
        self.status_dismiss_btn.setFixedSize(22, 22)
        self.status_dismiss_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.status_dismiss_btn.setToolTip("Dismiss notification")
        self.status_dismiss_btn.clicked.connect(self._dismiss_status)
        status_banner_layout.addWidget(self.status_dismiss_btn, 0, Qt.AlignmentFlag.AlignTop)

        self.status_banner.setVisible(False)
        layout.addWidget(self.status_banner)

        close_btn = QPushButton("Close")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        outer.addWidget(card)
        tag_theme_recursive(self, self.is_dark)

    def _build_pair_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(6, 14, 6, 6)

        hint = QLabel(
            "On your phone: Settings \u2192 Developer options \u2192 Wireless debugging "
            "\u2192 Pair device with pairing code. Enter what it shows below."
        )
        hint.setObjectName("SubHeaderLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.pair_host_input = QLineEdit()
        self.pair_host_input.setPlaceholderText("Pairing IP:port  (e.g. 192.168.1.20:41235)")
        layout.addWidget(self.pair_host_input)

        self.pair_code_input = QLineEdit()
        self.pair_code_input.setPlaceholderText("6-digit pairing code")
        layout.addWidget(self.pair_code_input)

        pair_btn = QPushButton("Pair")
        pair_btn.setObjectName("PrimaryButton")
        pair_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        pair_btn.clicked.connect(self._do_pair)
        layout.addWidget(pair_btn)

        divider = QLabel("Then connect using the regular Wireless debugging IP:port:")
        divider.setObjectName("SubHeaderLabel")
        divider.setWordWrap(True)
        layout.addWidget(divider)

        self.pair_connect_host_input = QLineEdit()
        self.pair_connect_host_input.setPlaceholderText("Connect IP:port  (e.g. 192.168.1.20:37020)")
        layout.addWidget(self.pair_connect_host_input)

        connect_btn = QPushButton("Connect")
        connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        connect_btn.clicked.connect(lambda: self._do_connect(self.pair_connect_host_input.text().strip()))
        layout.addWidget(connect_btn)

        layout.addStretch()
        return tab

    def _build_reconnect_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(6, 14, 6, 6)

        hint = QLabel(
            "Already paired this device before, or enabled TCP/IP mode over USB? "
            "Enter its Wi-Fi IP:port to reconnect."
        )
        hint.setObjectName("SubHeaderLabel")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.reconnect_host_input = QLineEdit()
        self.reconnect_host_input.setPlaceholderText("IP:port  (e.g. 192.168.1.20:5555)")
        layout.addWidget(self.reconnect_host_input)

        connect_btn = QPushButton("Connect")
        connect_btn.setObjectName("PrimaryButton")
        connect_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        connect_btn.clicked.connect(lambda: self._do_connect(self.reconnect_host_input.text().strip()))
        layout.addWidget(connect_btn)

        layout.addSpacing(6)
        usb_hint = QLabel(
            "No cable handy for the first pairing? If the phone is currently on USB, this "
            "enables Wi-Fi mode on it directly:"
        )
        usb_hint.setObjectName("SubHeaderLabel")
        usb_hint.setWordWrap(True)
        layout.addWidget(usb_hint)

        tcpip_btn = QPushButton("Enable Wi-Fi Mode via USB")
        tcpip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        tcpip_btn.clicked.connect(self._do_enable_tcpip)
        layout.addWidget(tcpip_btn)

        layout.addStretch()
        return tab

    def _show_status(self, message: str, is_error: bool):
        self.status_label.setText(("\u26a0 " if is_error else "\u2713 ") + message)
        self.status_banner.setObjectName("StatusBannerWarningContainer" if is_error else "StatusBannerNeutralContainer")
        self.status_label.setObjectName("StatusBannerWarning" if is_error else "StatusBannerNeutral")
        self.status_banner.style().unpolish(self.status_banner)
        self.status_banner.style().polish(self.status_banner)
        tag_theme_recursive(self.status_banner, self.is_dark)
        self.status_banner.setVisible(True)

    def _dismiss_status(self):
        self.status_banner.setVisible(False)
        self.status_label.setText("")

    def _do_pair(self):
        host = self.pair_host_input.text().strip()
        code = self.pair_code_input.text().strip()
        if not host or ":" not in host or not code:
            self._show_status("Enter both the pairing IP:port and the 6-digit code.", True)
            return
        ok, msg = self.adb_manager.pair_device(host, code)
        self._show_status(msg, not ok)

    def _do_connect(self, host: str):
        if not host or ":" not in host:
            self._show_status("Enter a valid IP:port, e.g. 192.168.1.20:5555.", True)
            return
        ok, msg = self.adb_manager.connect_wireless(host)
        self._show_status(msg, not ok)

    def _do_enable_tcpip(self):
        ok, msg = self.adb_manager.enable_tcpip_mode(5555)
        if ok:
            ip = self.adb_manager.get_device_wifi_ip()
            suffix = f" Device IP looks like {ip} \u2014 you can now unplug USB and connect to {ip}:5555." if ip else " You can now unplug USB and use Connect above with the phone's Wi-Fi IP and port 5555."
            self._show_status(msg + suffix, False)
        else:
            self._show_status(msg, True)
