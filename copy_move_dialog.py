# Copy vs Move confirmation dialog for Warp Transfer.
#
# FIX: Move existed only as a code path (TransferCoordinator's operation_type
# param, and the source-deletion logic in delete_source_items()) -- nothing
# in the UI ever actually offered it. Every trigger site hardcoded "copy".
# This dialog is the missing piece: shown for the two explicit "custom"
# transfer flows (Pull Custom Files via PhoneBrowserDialog, Push Files to
# Phone via a PC file picker) where the user is deliberately choosing what
# to transfer, so asking Copy-or-Move there is natural. The quick preset
# backup buttons (Quick Media Backup, etc.) and drag-and-drop stay Copy-only
# deliberately -- Move is a deliberate, slower-to-undo action that shouldn't
# be one accidental drag away.

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QWidget, QGraphicsDropShadowEffect)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from theme_utils import tag_theme_recursive


class CopyMoveDialog(QDialog):
    def __init__(self, item_count: int, is_dark: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Copy or Move?")
        self.setModal(True)
        self.setFixedSize(380, 260)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.result_mode = None  # "copy" | "move" | None (cancelled)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        card = QWidget(self)
        card.setObjectName("CardContainer")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(26, 24, 26, 24)
        layout.setSpacing(10)

        title = QLabel("Copy or Move?", card)
        title.setObjectName("HeaderLabel")
        title.setStyleSheet("font-size: 17px;")
        layout.addWidget(title)

        plural = "item" if item_count == 1 else "items"
        desc = QLabel(
            f"You've selected {item_count} {plural}. Copy keeps the originals in place; "
            f"Move deletes them from the source once the transfer is verified.",
            card,
        )
        desc.setObjectName("SubHeaderLabel")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

        copy_btn = QPushButton("Copy (keep originals)", card)
        copy_btn.setObjectName("PrimaryButton")
        copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        copy_btn.clicked.connect(lambda: self._choose("copy"))
        layout.addWidget(copy_btn)

        move_btn = QPushButton("Move (delete after transfer)", card)
        move_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        move_btn.clicked.connect(lambda: self._choose("move"))
        layout.addWidget(move_btn)

        cancel_btn = QPushButton("Cancel", card)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        outer.addWidget(card)
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        tag_theme_recursive(self, is_dark)

    def _choose(self, mode: str):
        self.result_mode = mode
        self.accept()

    @staticmethod
    def ask(item_count: int, is_dark: bool, parent=None) -> str:
        """Returns 'copy', 'move', or None if the user cancelled."""
        dlg = CopyMoveDialog(item_count, is_dark, parent)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            return dlg.result_mode
        return None
