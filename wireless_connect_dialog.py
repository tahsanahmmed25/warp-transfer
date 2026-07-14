# Wireless (Wi-Fi) ADB connection dialog for Warp Transfer.
#
# Two supported flows, matching how Android's wireless debugging actually
# works, exposed as two tabs:
#   1. "Pair New Device"   -- Android 11+. User opens Settings > Developer
#      options > Wireless debugging > Pair device with pairing code, which
#      shows an IP:port + 6-digit code. That's a one-time handshake; adb
#      pair completes it, then a normal adb connect to the *regular*
#      Wireless debugging IP:port (also shown on that same screen) attaches
#      the device going forward.
#   2. "Reconnect" -- for a device already paired this session (or on
#      Android <11 where enable_tcpip_mode() was used over USB first), just
#      adb connect to a known ip:port.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QWidget, QTabWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor


class WirelessConnectDialog(QDialog):
    def __init__(self, adb_manager, parent=None):
        super().__init__(parent)
        self.adb_manager = adb_manager
        self.setWindowTitle("Connect Wirelessly")
        self.setModal(True)
        self.setFixedSize(440, 380)
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
        title.setStyleSheet("font-size: 17px;")
        layout.addWidget(title)

        tabs = QTabWidget()
        tabs.addTab(self._build_pair_tab(), "Pair New Device")
        tabs.addTab(self._build_reconnect_tab(), "Reconnect")
        layout.addWidget(tabs)

        self.status_label = QLabel("")
        self.status_label.setObjectName("StatusBannerNeutral")
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)
        layout.addWidget(self.status_label)

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

    def _build_pair_tab(self) -> QWidget:
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(10)
        layout.setContentsMargins(4, 12, 4, 4)

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

        divider = QLabel("Then connect using the regular Wireless debugging IP:port shown on that same screen:")
        divider.setObjectName("PathLabel")
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
        layout.setContentsMargins(4, 12, 4, 4)

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
            "enables Wi-Fi mode on it directly (Android <11, or as a shortcut on newer versions):"
        )
        usb_hint.setObjectName("PathLabel")
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
        self.status_label.setObjectName("StatusBannerWarning" if is_error else "StatusBannerNeutral")
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)
        self.status_label.setVisible(True)

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
