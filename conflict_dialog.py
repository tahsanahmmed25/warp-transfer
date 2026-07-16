# Conflict-resolution dialog for Warp Transfer.
# Shown when a transfer is about to overwrite files that already exist at
# the destination and the user's default conflict mode is "Ask every time".

from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from theme_utils import tag_theme_recursive


class ConflictDialog(QDialog):
    """Modal dialog offering Skip / Overwrite / Rename / Cancel for a batch
    of file-name collisions detected before a transfer starts. Applies to
    the whole batch rather than prompting once per file, since transfers
    here commonly involve dozens-to-thousands of files."""

    def __init__(self, conflict_count: int, is_dark: bool, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Files Already Exist")
        self.setModal(True)
        self.setFixedSize(420, 260)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.chosen_mode = "cancel"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(16, 16, 16, 16)

        container = self._build_container(conflict_count)
        outer.addWidget(container)

        # FIX (queue item #1): `is_dark` was already being passed in but
        # never actually used -- this dialog always rendered with whichever
        # theme happened to be the QSS default, regardless of the app's
        # real current theme. Tag the whole dialog tree now that it's fully
        # built, same mechanism MainWindow uses on itself.
        tag_theme_recursive(self, is_dark)

    def _build_container(self, conflict_count):
        from PyQt6.QtWidgets import QWidget
        card = QWidget(self)
        card.setObjectName("CardContainer")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(28, 26, 28, 24)
        layout.setSpacing(14)

        title = QLabel(f"{conflict_count} file(s) already exist at the destination")
        title.setObjectName("HeaderLabel")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 17px;")
        layout.addWidget(title)

        desc = QLabel("Choose how to handle every conflicting file in this transfer.")
        desc.setObjectName("SubHeaderLabel")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addSpacing(6)

        skip_btn = QPushButton("Skip existing files")
        skip_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        skip_btn.clicked.connect(lambda: self._choose("skip"))
        layout.addWidget(skip_btn)

        rename_btn = QPushButton("Keep both (rename new file)")
        rename_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        rename_btn.clicked.connect(lambda: self._choose("rename"))
        layout.addWidget(rename_btn)

        overwrite_btn = QPushButton("Overwrite existing files")
        overwrite_btn.setObjectName("DangerButton")
        overwrite_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        overwrite_btn.clicked.connect(lambda: self._choose("overwrite"))
        layout.addWidget(overwrite_btn)

        cancel_btn = QPushButton("Cancel Transfer")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(lambda: self._choose("cancel"))
        layout.addWidget(cancel_btn)

        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(0, 0, 0, 120))
        card.setGraphicsEffect(shadow)

        return card

    def _choose(self, mode: str):
        self.chosen_mode = mode
        self.accept()

    @staticmethod
    def ask(conflict_count: int, is_dark: bool, parent=None) -> str:
        """Convenience helper: shows the dialog modally and returns the
        chosen mode string ('skip' | 'rename' | 'overwrite' | 'cancel')."""
        dlg = ConflictDialog(conflict_count, is_dark, parent)
        dlg.exec()
        return dlg.chosen_mode
