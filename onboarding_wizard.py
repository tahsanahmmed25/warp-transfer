# Onboarding Setup Wizard UI for Warp Transfer (PyQt6)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QSizePolicy,
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QSequentialAnimationGroup
from PyQt6.QtGui import QDesktopServices, QColor
from PyQt6.QtCore import QUrl
import re


def _md_to_richtext(text: str) -> str:
    """Convert lightweight **bold** markdown + newlines into safe HTML for QLabel rich text."""
    escaped = (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;"))
    bolded = re.sub(r"\*\*(.+?)\*\*", r"<b style='color:#D4AF37;'>\1</b>", escaped)
    return bolded.replace("\n", "<br>")


def make_rich_label(text: str, object_name: str = "SubHeaderLabel", parent=None) -> QLabel:
    label = QLabel(parent)
    label.setObjectName(object_name)
    label.setTextFormat(Qt.TextFormat.RichText)
    label.setText(_md_to_richtext(text))
    label.setWordWrap(True)
    return label


def _add_card_shadow(widget, blur=28, y_offset=8, alpha=70):
    """Soft elevation shadow for onboarding step cards, matching the
    dashboard's shadow treatment (see add_shadow in main.py)."""
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, y_offset)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)
    return shadow


class OnboardingWizard(QWidget):
    finished = pyqtSignal()
    # Emitted when the live status banner is showing "multiple devices" and
    # the user taps the Choose Device button that appears alongside it.
    choose_device_clicked = pyqtSignal()
    # Emitted when the banner is showing "disconnected" and the user taps
    # the Connect Wirelessly shortcut that appears alongside it.
    connect_wirelessly_clicked = pyqtSignal()

    def __init__(self, adb_manager):
        super().__init__()
        self.adb_manager = adb_manager
        self._fade_anim = None

        self.init_ui()

    def init_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(16)
        
        # Header title area
        self.title_label = QLabel("Set Up Your Android Device", self)
        self.title_label.setObjectName("HeaderLabel")
        self.layout.addWidget(self.title_label)

        # Live connection-status banner row: a status message plus a
        # context-specific action button that only appears for states where
        # there's something the user can immediately do beyond reading text
        # (choosing between multiple devices, or jumping to wireless connect
        # instead of hunting for a cable).
        banner_row = QHBoxLayout()
        banner_row.setSpacing(10)

        self.status_banner = QLabel("", self)
        self.status_banner.setObjectName("StatusBannerNeutral")
        self.status_banner.setWordWrap(True)
        self.status_banner.setVisible(False)
        banner_row.addWidget(self.status_banner, 1)

        self.banner_action_btn = QPushButton("", self)
        self.banner_action_btn.setObjectName("PrimaryButton")
        self.banner_action_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.banner_action_btn.setVisible(False)
        banner_row.addWidget(self.banner_action_btn)

        self.layout.addLayout(banner_row)
        
        # Stacked widget for wizard steps
        self.stacked_widget = QStackedWidget(self)
        self.stacked_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.layout.addWidget(self.stacked_widget)
        
        # Create wizard steps
        self.step1 = self.create_step_1()
        self.step2 = self.create_step_2()
        self.step3 = self.create_step_3()
        self.step4 = self.create_step_4()
        
        self.stacked_widget.addWidget(self.step1)
        self.stacked_widget.addWidget(self.step2)
        self.stacked_widget.addWidget(self.step3)
        self.stacked_widget.addWidget(self.step4)
        
        # Bottom Navigation bar
        self.nav_layout = QHBoxLayout()
        
        self.back_button = QPushButton("Back", self)
        self.back_button.clicked.connect(self.prev_step)
        self.back_button.setEnabled(False)
        self.nav_layout.addWidget(self.back_button)
        
        self.nav_layout.addStretch()
        
        # Status dots indicator
        self.dots_layout = QHBoxLayout()
        self.dots_layout.setSpacing(8)
        self.dots = []
        for i in range(4):
            dot = QWidget(self)
            dot.setFixedSize(10, 10)
            dot.setObjectName("DotInactive")
            self.dots_layout.addWidget(dot)
            self.dots.append(dot)
        self.update_dots(0)
        self.nav_layout.addLayout(self.dots_layout)
        
        self.nav_layout.addStretch()
        
        self.next_button = QPushButton("Next", self)
        self.next_button.setObjectName("PrimaryButton")
        self.next_button.clicked.connect(self.next_step)
        self.nav_layout.addWidget(self.next_button)
        
        self.layout.addLayout(self.nav_layout)

    def update_connection_status(self, status: str, device: str):
        """Live device-state feedback, called by MainWindow every poll tick
        while this wizard is the active page (plus once immediately when the
        page is first shown, so the banner isn't blank until the next tick).

        Surfaces the states AdbManager.check_devices() actually distinguishes:
        "unauthorized" (RSA fingerprint prompt not yet accepted), "multiple"
        (more than one device attached -- now pairs with a Choose Device
        button instead of just blocking), "offline" (unstable connection),
        and "disconnected" (nothing plugged in yet -- now pairs with a
        Connect Wirelessly shortcut for people without a cable handy).
        """
        try:
            self.banner_action_btn.clicked.disconnect()
        except TypeError:
            pass  # no connection existed yet -- fine, nothing to remove
        self.banner_action_btn.setVisible(False)

        if status == "unauthorized":
            self.status_banner.setText(
                "\u26a0 Device detected but not authorized yet \u2014 check your phone's screen "
                "and tap \u201cAllow\u201d on the USB debugging prompt."
            )
            new_name = "StatusBannerWarning"
            visible = True
        elif status == "multiple":
            label = device if device else "Multiple devices"
            self.status_banner.setText(f"\u26a0 {label} detected.")
            new_name = "StatusBannerWarning"
            visible = True
            self.banner_action_btn.setText("Choose Device")
            self.banner_action_btn.clicked.connect(self.choose_device_clicked.emit)
            self.banner_action_btn.setVisible(True)
        elif status == "offline":
            self.status_banner.setText(
                "\u26a0 Device connection is unstable \u2014 try unplugging and reconnecting the USB cable."
            )
            new_name = "StatusBannerWarning"
            visible = True
        elif status == "disconnected":
            self.status_banner.setText("Waiting for your phone to be connected via USB\u2026")
            new_name = "StatusBannerNeutral"
            visible = True
            self.banner_action_btn.setText("Connect Wirelessly")
            self.banner_action_btn.clicked.connect(self.connect_wirelessly_clicked.emit)
            self.banner_action_btn.setVisible(True)
        else:
            # "connected" (about to transition away to the dashboard) or any
            # unrecognized future status \u2014 nothing useful to show here.
            visible = False
            new_name = self.status_banner.objectName() or "StatusBannerNeutral"

        self.status_banner.setVisible(visible)
        if new_name != self.status_banner.objectName():
            self.status_banner.setObjectName(new_name)
            # Force stylesheet re-evaluation since the object name (and
            # therefore which QSS rule applies) changed at runtime.
            self.status_banner.style().unpolish(self.status_banner)
            self.status_banner.style().polish(self.status_banner)

    def create_step_1(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(20)
        
        # Card Container
        card = QWidget()
        card.setObjectName("CardContainer")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)
        
        # Step Number Badge
        badge_layout = QHBoxLayout()
        step_badge = QLabel("  STEP 1  ")
        step_badge.setObjectName("StepNumberLabel")
        step_badge.setFixedSize(65, 24)
        step_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_layout.addWidget(step_badge)
        badge_layout.addStretch()
        card_layout.addLayout(badge_layout)
        
        title = QLabel("Enable Developer Options", card)
        title.setObjectName("StepTitleLabel")
        card_layout.addWidget(title)
        
        desc = make_rich_label(
            "To transfer files at max USB speeds, we need to communicate with your phone.\n\n"
            "1. Open **Settings** on your phone.\n"
            "2. Go to **About Phone** (or About Device).\n"
            "3. Find the **Build Number** row and tap it **7 times**.\n"
            "4. A popup will say \"You are now a developer!\"",
            parent=card
        )
        card_layout.addWidget(desc)
        
        layout.addWidget(card)
        _add_card_shadow(card)
        return widget

    def create_step_2(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(20)
        
        card = QWidget()
        card.setObjectName("CardContainer")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)
        
        badge_layout = QHBoxLayout()
        step_badge = QLabel("  STEP 2  ")
        step_badge.setObjectName("StepNumberLabel")
        step_badge.setFixedSize(65, 24)
        step_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_layout.addWidget(step_badge)
        badge_layout.addStretch()
        card_layout.addLayout(badge_layout)
        
        title = QLabel("Turn On USB Debugging", card)
        title.setObjectName("StepTitleLabel")
        card_layout.addWidget(title)
        
        desc = make_rich_label(
            "Now let's enable the transfer toggle:\n\n"
            "1. Go back to your main **Settings** page.\n"
            "2. Search for **Developer Options** (often under System or Additional Settings).\n"
            "3. Scroll down and turn on **USB Debugging**.\n"
            "4. If prompted, tap **OK** to allow it.",
            parent=card
        )
        card_layout.addWidget(desc)
        
        layout.addWidget(card)
        _add_card_shadow(card)
        return widget

    def create_step_3(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(20)
        
        card = QWidget()
        card.setObjectName("CardContainer")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)
        
        badge_layout = QHBoxLayout()
        step_badge = QLabel("  STEP 3  ")
        step_badge.setObjectName("StepNumberLabel")
        step_badge.setFixedSize(65, 24)
        step_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_layout.addWidget(step_badge)
        badge_layout.addStretch()
        card_layout.addLayout(badge_layout)
        
        title = QLabel("Connect & Authorize", card)
        title.setObjectName("StepTitleLabel")
        card_layout.addWidget(title)
        
        desc = make_rich_label(
            "Connect your phone to your PC via a USB cable. Then check your phone's screen:\n\n"
            "1. A popup asking **\"Allow USB debugging?\"** will appear.\n"
            "2. Check **\"Always allow from this computer\"**.\n"
            "3. Tap **OK** or **Allow**.\n\n"
            "The app will automatically detect your phone once authorized!",
            parent=card
        )
        card_layout.addWidget(desc)
        
        layout.addWidget(card)
        _add_card_shadow(card)
        return widget

    def create_step_4(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(20)
        
        card = QWidget()
        card.setObjectName("CardContainer")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(30, 30, 30, 30)
        card_layout.setSpacing(15)
        
        badge_layout = QHBoxLayout()
        step_badge = QLabel(" HELP ")
        step_badge.setObjectName("StepNumberLabel")
        step_badge.setFixedSize(55, 24)
        step_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge_layout.addWidget(step_badge)
        badge_layout.addStretch()
        card_layout.addLayout(badge_layout)
        
        title = QLabel("Connection Troubleshooting", card)
        title.setObjectName("StepTitleLabel")
        card_layout.addWidget(title)
        
        desc = make_rich_label(
            "If your phone still isn't showing up, try these steps:\n\n"
            "\u2022 <b style='color:#D4AF37;'>Replug the Cable:</b> Unplug your USB cable, wait 3 seconds, and plug it back in.\n"
            "\u2022 <b style='color:#D4AF37;'>USB Connection Mode:</b> Swap your connection type on your phone notification bar from 'Charge only' to 'File Transfer'.\n"
            "\u2022 <b style='color:#D4AF37;'>MIUI / HyperOS Note:</b> Xiaomi/Redmi users must also enable the **\"USB debugging (Security settings)\"** toggle in Developer Options.\n"
            "\u2022 <b style='color:#D4AF37;'>No cable handy?</b> Use **Connect Wirelessly** (shown above while disconnected) to pair over Wi-Fi instead.\n"
            "\u2022 <b style='color:#D4AF37;'>Install Windows Drivers:</b> Some brands need drivers to connect. Click below to download the official Google driver:",
            parent=card
        )
        card_layout.addWidget(desc)
        
        driver_btn = QPushButton("Download Official USB Drivers", card)
        driver_btn.setObjectName("LinkButton")
        driver_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        driver_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://developer.android.com/studio/run/win-usb")))
        card_layout.addWidget(driver_btn)
        
        layout.addWidget(card)
        _add_card_shadow(card)
        return widget

    def update_dots(self, index):
        for idx, dot in enumerate(self.dots):
            if idx == index:
                dot.setObjectName("DotActive")
            else:
                dot.setObjectName("DotInactive")
            # Force stylesheet update
            dot.style().unpolish(dot)
            dot.style().polish(dot)

    def _fade_to_index(self, new_index):
        """Cross-fade the step transition instead of a hard cut, using an
        opacity effect on the incoming page. Keeps a reference to the
        animation so it isn't garbage-collected mid-flight."""
        self.stacked_widget.setCurrentIndex(new_index)
        incoming = self.stacked_widget.currentWidget()
        
        effect = QGraphicsOpacityEffect(incoming)
        incoming.setGraphicsEffect(effect)
        
        anim = QPropertyAnimation(effect, b"opacity", self)
        anim.setDuration(220)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.finished.connect(lambda: incoming.setGraphicsEffect(None))
        anim.start()
        
        self._fade_anim = anim

    def next_step(self):
        curr = self.stacked_widget.currentIndex()
        if curr < 3:
            self._fade_to_index(curr + 1)
            self.back_button.setEnabled(True)
            self.update_dots(curr + 1)
            if curr + 1 == 3:
                self.next_button.setText("Finish")
        else:
            self.finished.emit()

    def prev_step(self):
        curr = self.stacked_widget.currentIndex()
        if curr > 0:
            self._fade_to_index(curr - 1)
            self.next_button.setText("Next")
            self.update_dots(curr - 1)
            if curr - 1 == 0:
                self.back_button.setEnabled(False)
