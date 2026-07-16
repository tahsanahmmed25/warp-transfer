# Onboarding Setup Wizard UI for Warp Transfer (PyQt6)

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QStackedWidget, QSizePolicy,
                             QGraphicsDropShadowEffect, QGraphicsOpacityEffect,
                             QScrollArea)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QSequentialAnimationGroup, QEasingCurve, QSize
from PyQt6.QtGui import QDesktopServices, QColor, QPixmap, QPainter
from PyQt6.QtCore import QUrl
from PyQt6.QtSvg import QSvgRenderer
import re

from ui_transitions import fade_to_page
# QPropertyAnimation/QGraphicsOpacityEffect/QSequentialAnimationGroup were
# briefly removed (Phase 2 refactor moved step-fade logic out to
# ui_transitions.fade_to_page) but are back for two purposes: the
# Finish-button "pulse the banner" feedback in _pulse_banner() below, and
# the reconnect card's looping "listening for device" breathing animation
# (built inline in init_ui(), on self.reconnect_icon_badge). QEasingCurve IS
# used now, by that breathing animation, for a smoother sine-like pulse
# than a linear blink.

_SVG_PHONE = ('<svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" '
              'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
              'stroke-linejoin="round"><rect width="14" height="20" x="5" y="2" rx="2" ry="2"/>'
              '<line x1="12" x2="12.01" y1="18" y2="18"/></svg>')


def _phone_icon_pixmap(color: str, size: int = 28) -> QPixmap:
    """Small local SVG->QPixmap renderer, mirroring main.py's
    get_svg_pixmap/get_svg_content pattern but kept self-contained here
    rather than imported, since main.py imports OnboardingWizard (importing
    back the other way would be circular)."""
    pixmap = QPixmap(QSize(size, size))
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    QSvgRenderer(_SVG_PHONE.format(color=color).encode("utf-8")).render(painter)
    painter.end()
    return pixmap


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


def _wrap_in_scroll_area(widget: QWidget) -> QWidget:
    """Wrap a step's content in a borderless QScrollArea so content taller
    than the wizard's fixed window height (MainWindow.setFixedSize in
    main.py) scrolls instead of silently clipping. Confirmed necessary via
    a user screenshot of step 4 (Connection Troubleshooting): the
    'USB Connection Mode' bullet was cut off mid-sentence with no way to
    scroll down to read the rest or reach the driver-download button below
    it. Applied to every step, not just step 4, so any step's content
    growing past the visible area in the future degrades gracefully
    instead of clipping again."""
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setFrameShape(QScrollArea.Shape.NoFrame)
    scroll.setWidget(widget)
    return scroll


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
        self._banner_pulse_anim = None
        # PHASE 4 (localsend_parity_plan.md): once the person explicitly
        # taps "Show full setup guide" from the reconnect view, don't snap
        # back to the reconnect view on the very next poll tick just
        # because the device is still (correctly) reporting as known --
        # that would fight the person's own explicit choice. Reset only
        # when a genuinely new OnboardingWizard instance is built (i.e. a
        # fresh time the wizard page is shown from scratch).
        self._force_full_wizard = False

        self.init_ui()

    def init_ui(self):
        # Main layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(16)
        
        # Header title area
        self.title_label = QLabel("Set Up Your Android Device", self)
        self.title_label.setObjectName("HeaderLabel")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.title_label)

        # Live connection-status banner row: a status message plus a
        # context-specific action button that only appears for states where
        # there's something the user can immediately do beyond reading text
        # (choosing between multiple devices, or jumping to wireless connect
        # instead of hunting for a cable).
        self.banner_row_widget = QWidget(self)
        banner_row = QHBoxLayout(self.banner_row_widget)
        banner_row.setContentsMargins(0, 0, 0, 0)
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

        self.layout.addWidget(self.banner_row_widget)

        # PHASE 4 (localsend_parity_plan.md): lightweight reconnect view.
        # Shown INSTEAD of the full 4-step "how to enable Developer
        # Options" wizard for a device WarpTransfer has already seen
        # connect successfully before (tracked in MainWindow's persisted
        # config as known_devices: {device_id: friendly_name}) -- there's
        # no reason to walk someone through first-time setup instructions
        # every time a familiar phone's USB connection blips or gets
        # unplugged/replugged. Built once here, hidden until
        # update_connection_status() decides it applies.
        self.reconnect_widget = QWidget(self)
        reconnect_outer = QVBoxLayout(self.reconnect_widget)
        reconnect_outer.setContentsMargins(0, 20, 0, 20)
        
        reconnect_outer.addStretch(1)

        self.reconnect_card = QWidget()
        self.reconnect_card.setObjectName("CardContainer")
        rc_layout = QVBoxLayout(self.reconnect_card)
        rc_layout.setContentsMargins(40, 36, 40, 36)
        rc_layout.setSpacing(14)
        # NOTE (Session N+18): do NOT set alignment on this layout itself.
        # Sessions N+16/N+17 found and fixed this exact mechanism one level
        # up on `reconnect_outer` (the wrapper around the whole card) -- a
        # QVBoxLayout with alignment set gets constrained to its sizeHint
        # instead of stretching to fill available space, which starves a
        # word-wrapped label of the extra row height it needs once its text
        # grows from 1 line to 2 (e.g. "Reconnect your device" ->
        # "Reconnect your Redmi Note 7 Pro"), producing the
        # overlapping/squeezed title text from the screenshots. That fix
        # never actually resolved the reported bug because THIS layout --
        # rc_layout, the card's own internal layout one level deeper than
        # reconnect_outer -- had the identical setAlignment(AlignCenter)
        # call, reproducing the same squeeze independently. Each child
        # widget already centers its own text via its own
        # setAlignment(AlignCenter) call (reconnect_title, reconnect_desc,
        # etc.), so this layout doesn't need alignment itself to stay
        # visually centered -- a QVBoxLayout with no alignment set already
        # stretches children to the container's full width by default.

        self.reconnect_title = QLabel("Reconnect your device", self.reconnect_card)
        self.reconnect_title.setObjectName("HeaderLabel")
        self.reconnect_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reconnect_title.setWordWrap(True)

        # A static card with just text read as flat/lifeless on real-device
        # screenshots. A small badge with a gentle looping "breathing" pulse
        # gives the screen a sense of "actively listening for your phone"
        # rather than a dead waiting-room screen -- cheap to build (reuses
        # the same IconBadge look as the dashboard) and keeps this screen's
        # calm, uncluttered feel rather than adding busy motion.
        self.reconnect_icon_badge = QWidget(self.reconnect_card)
        self.reconnect_icon_badge.setObjectName("IconBadge")
        self.reconnect_icon_badge.setFixedSize(56, 56)
        icon_badge_layout = QVBoxLayout(self.reconnect_icon_badge)
        icon_badge_layout.setContentsMargins(0, 0, 0, 0)
        icon_badge_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reconnect_icon_label = QLabel(self.reconnect_icon_badge)
        self.reconnect_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # A mid-tone gold reads clearly against both the dark and light
        # CardContainer background, so this doesn't need to track theme
        # changes the way main.py's SVG icons do.
        self.reconnect_icon_label.setPixmap(_phone_icon_pixmap("#C9A227", 28))
        icon_badge_layout.addWidget(self.reconnect_icon_label)
        rc_layout.addWidget(self.reconnect_icon_badge, 0, Qt.AlignmentFlag.AlignCenter)
        rc_layout.addSpacing(6)

        rc_layout.addWidget(self.reconnect_title)

        self.reconnect_desc = QLabel(
            "Plug your phone back in via USB \u2014 WarpTransfer will pick it up automatically, "
            "no setup needed.",
            self.reconnect_card,
        )
        self.reconnect_desc.setObjectName("SubHeaderLabel")
        self.reconnect_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reconnect_desc.setWordWrap(True)
        rc_layout.addWidget(self.reconnect_desc)

        self.reconnect_status_label = QLabel("", self.reconnect_card)
        self.reconnect_status_label.setObjectName("PathLabel")
        self.reconnect_status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.reconnect_status_label.setVisible(False)
        rc_layout.addWidget(self.reconnect_status_label)

        rc_layout.addSpacing(4)

        full_guide_btn = QPushButton("This is a different device \u2014 show full setup guide", self.reconnect_card)
        full_guide_btn.setObjectName("GhostTextLink")
        full_guide_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        full_guide_btn.clicked.connect(self._show_full_wizard_forced)
        rc_layout.addWidget(full_guide_btn)

        reconnect_outer.addWidget(self.reconnect_card)
        _add_card_shadow(self.reconnect_card)
        reconnect_outer.addStretch(1)

        self.reconnect_widget.setVisible(False)
        self.layout.addWidget(self.reconnect_widget)
        
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
        self.nav_widget = QWidget(self)
        self.nav_layout = QHBoxLayout(self.nav_widget)
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        self.layout.addWidget(self.nav_widget)

    def _show_full_wizard_forced(self):
        """The reconnect view's escape hatch -- forces the normal full
        wizard content visible and keeps it that way (see
        self._force_full_wizard docstring) until this OnboardingWizard
        instance is torn down and rebuilt fresh."""
        self._force_full_wizard = True
        self._set_reconnect_view_visible(False)

    def _set_reconnect_view_visible(self, show: bool):
        """Toggle between the lightweight reconnect card and the normal
        full step-wizard + nav bar. The live status banner row stays
        hidden while the reconnect view is showing -- both surfaces
        explaining connection state at once would be redundant messaging
        for what's meant to be a much calmer, lighter screen."""
        self.reconnect_widget.setVisible(show)
        self.stacked_widget.setVisible(not show)
        self.nav_widget.setVisible(not show)
        if show:
            self.banner_row_widget.setVisible(False)

    def _refresh_reconnect_shadow(self):
        """Force the reconnect card to fully re-layout and re-render after
        reconnect_title's text changes length.

        Real root cause (found after the previous shadow-cache-only fix did
        NOT resolve the reported ghosting -- confirmed by a second pair of
        screenshots showing the identical overlap): this wizard sits inside
        MainWindow's FIXED-size window (`setFixedSize`, see Session N+9).
        QLabel.setText() on a word-wrapped label normally re-triggers its
        own heightForWidth recalculation, but the enclosing QVBoxLayout
        (`rc_layout`) had already been laid out once against the SHORT
        placeholder text ("Reconnect your device", 1 line) before any real
        device name was known. When the text later grows to something that
        wraps onto 2 lines ("Reconnect your Redmi Note 7 Pro"), nothing
        told that already-laid-out row to reserve more height for it --
        Qt doesn't automatically re-run layout for an already-sized
        container just because a descendant's sizeHint changed, especially
        under a fixed-size top-level window. With AlignCenter set on the
        label, the result is the 2-line block getting vertically centered
        and squeezed into the OLD 1-line-tall allocated rect, producing the
        overlapping/garbled look from the screenshots.

        Fixed by explicitly invalidating and re-activating the layout chain
        (title -> card -> reconnect_widget) so Qt recomputes real heights
        within the existing fixed window bounds. Also tears down and
        rebuilds the card's QGraphicsDropShadowEffect as a defensive
        measure against any stale effect-source pixmap, since that effect
        renders based on the card's current geometry and could otherwise
        cache a stale frame from before the relayout."""
        self.reconnect_title.updateGeometry()
        if self.reconnect_card.layout() is not None:
            self.reconnect_card.layout().activate()
        self.reconnect_card.updateGeometry()
        self.reconnect_card.adjustSize()
        if self.reconnect_widget.layout() is not None:
            self.reconnect_widget.layout().activate()
        self.reconnect_widget.updateGeometry()

        self.reconnect_card.setGraphicsEffect(None)
        _add_card_shadow(self.reconnect_card)

    def update_connection_status(self, status: str, device: str, known_devices: dict = None):
        """Live device-state feedback, called by MainWindow every poll tick
        while this wizard is the active page (plus once immediately when the
        page is first shown, so the banner isn't blank until the next tick).

        Surfaces the states AdbManager.check_devices() actually distinguishes:
        "unauthorized" (RSA fingerprint prompt not yet accepted), "multiple"
        (more than one device attached -- now pairs with a Choose Device
        button instead of just blocking), "offline" (unstable connection),
        and "disconnected" (nothing plugged in yet -- now pairs with a
        Connect Wirelessly shortcut for people without a cable handy).

        PHASE 4 addition: `known_devices` (dict of {device_id: friendly_name},
        from MainWindow's persisted config) lets this method show the light
        reconnect view instead of the full first-time wizard for a device
        that's connected successfully before. Only applies to "disconnected"
        and "offline" -- "unauthorized" always needs the phone-side Allow
        prompt regardless of history, so it always shows the real banner
        (with a small reassurance line added when the device is recognized).
        """
        known_devices = known_devices or {}

        if self._force_full_wizard:
            self._set_reconnect_view_visible(False)
        elif status == "disconnected" and known_devices:
            self._set_reconnect_view_visible(True)
            if len(known_devices) == 1:
                name = next(iter(known_devices.values()))
                new_title = f"Reconnect your {name}"
            else:
                new_title = "Reconnect your device"
            if self.reconnect_title.text() != new_title:
                self.reconnect_title.setText(new_title)
                self._refresh_reconnect_shadow()
            self.reconnect_status_label.setVisible(False)
            return
        elif status == "offline" and device in known_devices:
            self._set_reconnect_view_visible(True)
            new_title = f"Reconnecting to {known_devices[device]}\u2026"
            if self.reconnect_title.text() != new_title:
                self.reconnect_title.setText(new_title)
                self._refresh_reconnect_shadow()
            self.reconnect_status_label.setText(
                "\u26a0 Connection is unstable \u2014 try unplugging and reconnecting the USB cable."
            )
            self.reconnect_status_label.setVisible(True)
            return
        else:
            self._set_reconnect_view_visible(False)

        self.banner_row_widget.setVisible(True)

        try:
            self.banner_action_btn.clicked.disconnect()
        except TypeError:
            pass  # no connection existed yet -- fine, nothing to remove
        self.banner_action_btn.setVisible(False)

        if status == "unauthorized":
            recognized_note = ""
            if device in known_devices:
                # Small reassurance for a device we've definitely seen
                # before -- this specific state can't be skipped (Android
                # always re-prompts per PC the first time in a session/after
                # a key reset), but knowing it's not a mystery first-time
                # setup step is worth saying.
                recognized_note = " You've connected this device before, so this should be quick."
            self.status_banner.setText(
                "\u26a0 Device detected but not authorized yet \u2014 check your phone's screen "
                f"and tap \u201cAllow\u201d on the USB debugging prompt.{recognized_note}"
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

    def _pulse_banner(self):
        """Brief attention-grabbing opacity blink on the status banner.
        Used when Finish is clicked on the last step but no device is
        actually connected yet -- previously that click silently did
        nothing (there's no dashboard to advance to without a device),
        which read as a broken button rather than "please connect your
        phone first", even though the banner above already explains why.
        Keeps the animation group on self._banner_pulse_anim so it isn't
        garbage-collected mid-flight."""
        effect = QGraphicsOpacityEffect(self.status_banner)
        self.status_banner.setGraphicsEffect(effect)

        group = QSequentialAnimationGroup(self)
        for _ in range(2):
            fade_out = QPropertyAnimation(effect, b"opacity")
            fade_out.setDuration(120)
            fade_out.setStartValue(1.0)
            fade_out.setEndValue(0.25)
            fade_in = QPropertyAnimation(effect, b"opacity")
            fade_in.setDuration(120)
            fade_in.setStartValue(0.25)
            fade_in.setEndValue(1.0)
            group.addAnimation(fade_out)
            group.addAnimation(fade_in)

        group.finished.connect(lambda: self.status_banner.setGraphicsEffect(None))
        group.start()
        self._banner_pulse_anim = group

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
        return _wrap_in_scroll_area(widget)

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
        return _wrap_in_scroll_area(widget)

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
        return _wrap_in_scroll_area(widget)

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
            "\u2022 **Replug the Cable:** Unplug your USB cable, wait 3 seconds, and plug it back in.\n"
            "\u2022 **USB Connection Mode:** Swap your connection type on your phone notification bar from 'Charge only' to 'File Transfer'.\n"
            "\u2022 **MIUI / HyperOS Note:** Xiaomi/Redmi users must also enable the **\"USB debugging (Security settings)\"** toggle in Developer Options.\n"
            "\u2022 **No cable handy?** Use **Connect Wirelessly** (shown above while disconnected) to pair over Wi-Fi instead.\n"
            "\u2022 **Install Windows Drivers:** Some brands need drivers to connect. Click below to download the official Google driver:",
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
        return _wrap_in_scroll_area(widget)

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
        """Cross-fade the step transition instead of a hard cut. Thin wrapper
        around the shared `fade_to_page` helper (ui_transitions.py) -- this
        method used to own the fade logic directly, but it's now shared with
        MainWindow's page transitions (Phase 2 of localsend_parity_plan.md).
        Keeps a reference to the returned animation on self._fade_anim so it
        isn't garbage-collected mid-flight (fade_to_page's own docstring
        explains why that's the caller's job, not the helper's)."""
        self._fade_anim = fade_to_page(self.stacked_widget, new_index)

    def next_step(self):
        curr = self.stacked_widget.currentIndex()
        if curr < 3:
            self._fade_to_index(curr + 1)
            self.back_button.setEnabled(True)
            self.update_dots(curr + 1)
            if curr + 1 == 3:
                self.next_button.setText("Finish")
        else:
            # Finish only actually advances if a device is connected --
            # there's no dashboard to go to otherwise. Previously this just
            # called self.finished.emit() unconditionally, which MainWindow's
            # show_onboarding_or_dashboard() slot would then find nothing to
            # do with (status != "connected" -> show_onboarding_page() again,
            # a same-widget no-op) -- silent to the user, looked like a dead
            # button. Now checks status directly and, if not connected,
            # refreshes + pulses the status banner instead so the "why" is
            # visibly obvious rather than nothing happening at all.
            status, device = self.adb_manager.check_devices()
            if status != "connected":
                self.update_connection_status(status, device)
                self._pulse_banner()
                return
            self.finished.emit()

    def prev_step(self):
        curr = self.stacked_widget.currentIndex()
        if curr > 0:
            self._fade_to_index(curr - 1)
            self.next_button.setText("Next")
            self.update_dots(curr - 1)
            if curr - 1 == 0:
                self.back_button.setEnabled(False)
