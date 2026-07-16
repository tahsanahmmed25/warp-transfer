# Device-picker dialog for Warp Transfer.
# Shown when AdbManager.check_devices() reports "multiple" -- instead of
# hard-blocking the user, let them choose which attached device to target.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QWidget, QScrollArea, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from theme_utils import tag_theme_recursive


class DevicePickerDialog(QDialog):
    def __init__(self, devices: list, is_dark: bool, parent=None):
        """devices: list of {"id","status","model"} dicts from
        AdbManager.list_all_devices()."""
        super().__init__(parent)
        self.setWindowTitle("Choose a Device")
        self.setModal(True)
        self.setFixedSize(420, 420)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.selected_device_id = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        card = QWidget(self)
        card.setObjectName("CardContainer")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(12)

        title = QLabel("Multiple Devices Detected")
        title.setObjectName("HeaderLabel")
        title.setStyleSheet("font-size: 17px;")
        layout.addWidget(title)

        desc = QLabel("Pick which device Warp Transfer should use for this session.")
        desc.setObjectName("SubHeaderLabel")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        list_layout.setSpacing(8)
        list_layout.setContentsMargins(0, 4, 0, 4)

        for d in devices:
            list_layout.addWidget(self._build_device_row(d))
        list_layout.addStretch()

        scroll.setWidget(list_widget)
        layout.addWidget(scroll)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        outer.addWidget(card)

        # FIX (queue item #1): this dialog previously had NO is_dark
        # parameter at all -- it always rendered with whatever the QSS
        # default happened to be, same class of gap as ConflictDialog but
        # this one didn't even have the parameter plumbed through yet.
        tag_theme_recursive(self, is_dark)

    def _build_device_row(self, device: dict) -> QWidget:
        row = QPushButton()
        row.setObjectName("QuickActionButton")
        row.setCursor(Qt.CursorShape.PointingHandCursor)
        row.setFixedHeight(64)

        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(4, 2, 4, 2)
        row_layout.setSpacing(2)

        status = device.get("status", "unknown")
        model = device.get("model", device.get("id", "Unknown device"))

        name_label = QLabel(model)
        name_label.setObjectName("QuickActionButtonTitle")
        row_layout.addWidget(name_label)

        status_text = {
            "device": "Ready \u2022 authorized",
            "unauthorized": "Not authorized \u2014 check phone screen",
            "offline": "Offline / unstable connection",
        }.get(status, status)
        status_label = QLabel(f"{device.get('id', '')}  \u2022  {status_text}")
        status_label.setObjectName("QuickActionButtonDesc")
        row_layout.addWidget(status_label)

        row.setEnabled(status == "device")
        row.clicked.connect(lambda: self._select(device.get("id")))
        return row

    def _select(self, device_id):
        self.selected_device_id = device_id
        self.accept()

    @staticmethod
    def ask(devices: list, is_dark: bool, parent=None):
        """Returns the chosen device id, or None if cancelled / nothing
        selectable."""
        selectable = [d for d in devices if d.get("status") == "device"]
        if not selectable:
            return None
        if len(selectable) == 1:
            return selectable[0]["id"]
        dlg = DevicePickerDialog(devices, is_dark, parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.selected_device_id
        return None
