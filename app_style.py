# Design System & Styling definitions for Warp Transfer (PyQt6 QSS)
# v3 -- Phase 3 rewrite: single merged stylesheet using a `theme` dynamic
# QSS property ("dark" / "light") instead of two separate full stylesheet
# strings swapped via QApplication.setStyleSheet(). This is loaded ONCE at
# startup (see main.py's init_ui) and never re-applied on toggle -- toggling
# theme now just flips the `theme` property + unpolish()/polish() on every
# widget, which only re-matches selectors instead of re-parsing/re-cascading
# the whole stylesheet string from scratch.
#
# Every selector that used to differ between APP_STYLE_DARK/APP_STYLE_LIGHT
# now has a [theme="dark"] and a [theme="light"] variant here. Anything that
# was identical between the two themes (radii, paddings, structural rules)
# stays theme-agnostic and unqualified.

APP_STYLE = """
/* Global Styles */
QMainWindow[theme="dark"] {
    background-color: #0C0C0E;
}
QMainWindow[theme="light"] {
    background-color: #F2F2F7;
}

QWidget {
    font-family: "Segoe UI Variable Text", "Segoe UI", "Inter", -apple-system, sans-serif;
    font-size: 13px;
}
QWidget[theme="dark"] {
    color: #F2F2F7;
}
QWidget[theme="light"] {
    color: #1C1C1E;
}

QToolTip[theme="dark"] {
    background-color: #1D1D24;
    color: #F2F2F7;
    border: 1px solid #2B2B35;
    border-radius: 6px;
    padding: 6px 10px;
}
QToolTip[theme="light"] {
    background-color: #FFFFFF;
    color: #1C1C1E;
    border: 1px solid #E5E5EA;
    border-radius: 6px;
    padding: 6px 10px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}
QScrollBar:vertical[theme="dark"] {
    background-color: #121214;
}
QScrollBar:vertical[theme="light"] {
    background-color: #E5E5EA;
}
QScrollBar::handle:vertical {
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical[theme="dark"] {
    background-color: #2D2D34;
}
QScrollBar::handle:vertical[theme="light"] {
    background-color: #C7C7CC;
}
QScrollBar::handle:vertical[theme="dark"]:hover {
    background-color: #D4AF37;
}
QScrollBar::handle:vertical[theme="light"]:hover {
    background-color: #B8860B;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Frameless Window Header / TitleBar */
#TitleBar[theme="dark"] {
    background-color: #121214;
    border-bottom: 1px solid #1F1F24;
}
#TitleBar[theme="light"] {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E5EA;
}
#TitleLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", "Inter", sans-serif;
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.2px;
}
#TitleLabel[theme="dark"] {
    color: #F2F2F7;
}
#TitleLabel[theme="light"] {
    color: #1C1C1E;
}
#LogoBadge[theme="dark"] {
    background-color: rgba(212, 175, 55, 0.14);
    border: 1px solid rgba(212, 175, 55, 0.35);
    border-radius: 9px;
}
#LogoBadge[theme="light"] {
    background-color: rgba(184, 134, 11, 0.10);
    border: 1px solid rgba(184, 134, 11, 0.30);
    border-radius: 9px;
}

/* Titlebar window control buttons */
#TitleBarButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
}
#TitleBarButton[theme="dark"]:hover {
    background-color: #23232B;
}
#TitleBarButton[theme="dark"]:pressed {
    background-color: #1A1A20;
}
#TitleBarButton[theme="light"]:hover {
    background-color: #EDEDF2;
}
#TitleBarButton[theme="light"]:pressed {
    background-color: #E2E2E8;
}
#CloseButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
}
#CloseButton[theme="dark"]:hover {
    background-color: #E5484D;
}
#CloseButton[theme="dark"]:pressed {
    background-color: #C23A3E;
}
#CloseButton[theme="light"]:hover {
    background-color: #FF3B30;
}
#CloseButton[theme="light"]:pressed {
    background-color: #D93227;
}

/* Navigation & Progress Dots */
#DotActive[theme="dark"] {
    background-color: #D4AF37;
    border-radius: 4px;
}
#DotActive[theme="light"] {
    background-color: #B8860B;
    border-radius: 4px;
}
#DotInactive[theme="dark"] {
    background-color: #2D2D34;
    border-radius: 4px;
}
#DotInactive[theme="light"] {
    background-color: #D1D1D6;
    border-radius: 4px;
}

/* Cards & Containers */
#CardContainer[theme="dark"] {
    background-color: #16161A;
    border: 1px solid #23232A;
    border-radius: 16px;
}
#CardContainer[theme="light"] {
    background-color: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 16px;
}

#InnerCard[theme="dark"] {
    background-color: #1B1B21;
    border: 1px solid #29293380;
    border-radius: 14px;
}
#InnerCard[theme="light"] {
    background-color: #FFFFFF;
    border: 1px solid #E9E9EE;
    border-radius: 14px;
}

/* OnboardingWizard live connection-status banner */
#StatusBannerWarning {
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
}
#StatusBannerWarning[theme="dark"] {
    background-color: rgba(224, 122, 63, 0.12);
    border: 1px solid rgba(224, 122, 63, 0.35);
    color: #E0A15E;
}
#StatusBannerWarning[theme="light"] {
    background-color: rgba(196, 106, 41, 0.10);
    border: 1px solid rgba(196, 106, 41, 0.30);
    color: #A85A24;
}
#StatusBannerNeutral {
    border-radius: 10px;
    padding: 10px 14px;
    font-size: 13px;
}
#StatusBannerNeutral[theme="dark"] {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid #29293380;
    color: #9C9CA6;
}
#StatusBannerNeutral[theme="light"] {
    background-color: rgba(0, 0, 0, 0.03);
    border: 1px solid #E9E9EE;
    color: #6E6E76;
}

#IconBadge[theme="dark"] {
    background-color: rgba(212, 175, 55, 0.12);
    border: 1px solid rgba(212, 175, 55, 0.28);
    border-radius: 11px;
}
#IconBadge[theme="light"] {
    background-color: rgba(184, 134, 11, 0.10);
    border: 1px solid rgba(184, 134, 11, 0.25);
    border-radius: 11px;
}

/* Labels */
#HeaderLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", "Inter", sans-serif;
    font-weight: 700;
    font-size: 24px;
}
#HeaderLabel[theme="dark"] {
    color: #FFFFFF;
}
#HeaderLabel[theme="light"] {
    color: #1C1C1E;
}

#SubHeaderLabel {
    font-size: 14px;
    line-height: 20px;
}
#SubHeaderLabel[theme="dark"] {
    color: #A9A9B2;
}
#SubHeaderLabel[theme="light"] {
    color: #58585C;
}

#StepTitleLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-weight: 700;
    font-size: 18px;
}
#StepTitleLabel[theme="dark"] {
    color: #FFFFFF;
}
#StepTitleLabel[theme="light"] {
    color: #1C1C1E;
}

#StatusLabel {
    font-weight: 600;
}
#StatusLabel[theme="dark"] {
    color: #D4AF37;
}
#StatusLabel[theme="light"] {
    color: #B8860B;
}

#SuccessStatusLabel {
    font-weight: 600;
    font-size: 11px;
}
#SuccessStatusLabel[theme="dark"] {
    color: #34C759;
}
#SuccessStatusLabel[theme="light"] {
    color: #248A3D;
}

#StepNumberLabel {
    border-radius: 12px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
}
#StepNumberLabel[theme="dark"] {
    background-color: #23232A;
    border: 1px solid #35353F;
    color: #D4AF37;
}
#StepNumberLabel[theme="light"] {
    background-color: #F2F2F7;
    border: 1px solid #E1E1E6;
    color: #B8860B;
}

#PathLabel {
    font-size: 12px;
}
#PathLabel[theme="dark"] {
    color: #9C9CA3;
}
#PathLabel[theme="light"] {
    color: #86868B;
}

#DestHeaderLabel {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.4px;
}
#DestHeaderLabel[theme="dark"] {
    color: #7C7C84;
}
#DestHeaderLabel[theme="light"] {
    color: #86868B;
}

#DragDropTitleLabel {
    font-weight: 600;
    font-size: 13px;
}
#DragDropTitleLabel[theme="dark"] {
    color: #E4E4E7;
}
#DragDropTitleLabel[theme="light"] {
    color: #1C1C1E;
}

#DragDropSubtextLabel {
    color: #8E8E93;
    font-size: 11px;
}

#DeviceTitleLabel {
    font-weight: 700;
    font-size: 15px;
}
#DeviceTitleLabel[theme="dark"] {
    color: #FFFFFF;
}
#DeviceTitleLabel[theme="light"] {
    color: #1C1C1E;
}

#TransferDetailLabel {
    font-size: 13px;
    font-weight: 600;
}
#TransferDetailLabel[theme="dark"] {
    color: #E4E4E7;
}
#TransferDetailLabel[theme="light"] {
    color: #1C1C1E;
}

#TransferFileLabel {
    color: #8E8E93;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    border-radius: 10px;
    padding: 9px 18px;
    font-weight: 600;
}
QPushButton[theme="dark"] {
    background-color: #1E1E24;
    border: 1px solid #2D2D39;
    color: #F2F2F7;
}
QPushButton[theme="dark"]:hover {
    background-color: #26262E;
    border-color: #3D3D4E;
}
QPushButton[theme="dark"]:pressed {
    background-color: #141418;
}
QPushButton[theme="dark"]:disabled {
    background-color: #121214;
    border-color: #1A1A1E;
    color: #48484A;
}
QPushButton[theme="light"] {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    color: #1C1C1E;
}
QPushButton[theme="light"]:hover {
    background-color: #F5F5F7;
    border-color: #C7C7CC;
}
QPushButton[theme="light"]:pressed {
    background-color: #E5E5EA;
}
QPushButton[theme="light"]:disabled {
    background-color: #F2F2F7;
    border-color: #E5E5EA;
    color: #AEAEB2;
}

/* Primary Call to Action Button */
#PrimaryButton {
    padding: 9px 22px;
}
#PrimaryButton[theme="dark"] {
    background-color: #D4AF37;
    border: 1px solid #E5C158;
    color: #14140E;
}
#PrimaryButton[theme="dark"]:hover {
    background-color: #E0BC4C;
    border-color: #F3D279;
}
#PrimaryButton[theme="dark"]:pressed {
    background-color: #B89327;
}
#PrimaryButton[theme="dark"]:disabled {
    background-color: #3A3423;
    border-color: #3A3423;
    color: #706A54;
}
#PrimaryButton[theme="light"] {
    background-color: #B8860B;
    border: 1px solid #A0720A;
    color: #FFFFFF;
}
#PrimaryButton[theme="light"]:hover {
    background-color: #CD9A13;
    border-color: #B8860B;
}
#PrimaryButton[theme="light"]:pressed {
    background-color: #8B6508;
}
#PrimaryButton[theme="light"]:disabled {
    background-color: #EAE0C8;
    border-color: #EAE0C8;
    color: #B8AD8E;
}

/* Secondary/Danger Button */
#DangerButton[theme="dark"] {
    background-color: #2A1415;
    border: 1px solid #4D2022;
    color: #FF6961;
}
#DangerButton[theme="dark"]:hover {
    background-color: #3D1C1E;
    border-color: #6E2D30;
}
#DangerButton[theme="dark"]:pressed {
    background-color: #1F0D0E;
}
#DangerButton[theme="dark"]:disabled {
    background-color: #1A1112;
    border-color: #2A1A1B;
    color: #6B4344;
}
#DangerButton[theme="light"] {
    background-color: #FDF2F2;
    border: 1px solid #F5C2C2;
    color: #E0342A;
}
#DangerButton[theme="light"]:hover {
    background-color: #FBE5E5;
    border-color: #F1A5A5;
}
#DangerButton[theme="light"]:pressed {
    background-color: #F7D0D0;
}
#DangerButton[theme="light"]:disabled {
    background-color: #FAF3F3;
    border-color: #F0DCDC;
    color: #D9A8A8;
}

/* Quick Action Buttons (Large layout) */
#QuickActionButton {
    border-radius: 14px;
    padding: 16px;
    text-align: left;
}
#QuickActionButton[theme="dark"] {
    background-color: #17171B;
    border: 1px solid #24242C;
}
#QuickActionButton[theme="dark"]:hover {
    border-color: #D4AF37;
    background-color: #1C1C21;
}
#QuickActionButton[theme="dark"]:pressed {
    background-color: #131316;
}
#QuickActionButton[theme="light"] {
    background-color: #FFFFFF;
    border: 1px solid #E5E5EA;
}
#QuickActionButton[theme="light"]:hover {
    border-color: #B8860B;
    background-color: #FCFAF4;
}
#QuickActionButton[theme="light"]:pressed {
    background-color: #F5F2E8;
}
#QuickActionButtonTitle {
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-weight: 700;
    font-size: 14px;
}
#QuickActionButtonTitle[theme="dark"] {
    color: #FFFFFF;
}
#QuickActionButtonTitle[theme="light"] {
    color: #1C1C1E;
}
#QuickActionButtonDesc {
    color: #8E8E93;
    font-size: 11px;
}

/* Drag and Drop Zone */
#DropZone[theme="dark"] {
    background-color: #131317;
    border: 2px dashed #2C2C36;
    border-radius: 16px;
}
#DropZone[theme="light"] {
    background-color: #F8F8FA;
    border: 2px dashed #D1D1D6;
    border-radius: 16px;
}
#DropZone[theme="dark"][dragActive="true"] {
    border-color: #D4AF37;
    background-color: #1E1B10;
}
#DropZone[theme="light"][dragActive="true"] {
    border-color: #B8860B;
    background-color: #FBF6E9;
}

/* Progress bar */
QProgressBar {
    border-radius: 7px;
    text-align: center;
    color: transparent;
}
QProgressBar[theme="dark"] {
    background-color: #1A1A1F;
    border: 1px solid #26262E;
}
QProgressBar[theme="light"] {
    background-color: #E9E9EE;
    border: 1px solid #DBDBE1;
}
QProgressBar[theme="dark"]::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #B8860B, stop:1 #E5C158);
    border-radius: 6px;
}
QProgressBar[theme="light"]::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #B8860B, stop:1 #D9A82B);
    border-radius: 6px;
}

/* Secondary outline button used for links/downloads */
#LinkButton {
    background-color: transparent;
    font-weight: 600;
}
#LinkButton[theme="dark"] {
    border: 1px solid #2D2D39;
    color: #D4AF37;
}
#LinkButton[theme="dark"]:hover {
    background-color: #1C1C21;
    border-color: #D4AF37;
}
#LinkButton[theme="light"] {
    border: 1px solid #D1D1D6;
    color: #B8860B;
}
#LinkButton[theme="light"]:hover {
    background-color: #FCFAF4;
    border-color: #B8860B;
}

/* Plain high-contrast text link (reconnect card's "different device" escape
   hatch). Deliberately NOT #LinkButton: that style's thin 1px border +
   gold-on-transparent text reads as washed out on a plain card background
   (confirmed via real-device screenshot -- "barely visible"). This is
   borderless/background-less by default so it reads as a link, not a
   competing secondary button, with a clearly darker/lighter (not just
   thinner) color shift + underline on hover for an obvious affordance. */
#GhostTextLink {
    background-color: transparent;
    border: none;
    font-weight: 700;
    padding: 4px 2px;
}
#GhostTextLink[theme="dark"] {
    color: #E8C766;
}
#GhostTextLink[theme="dark"]:hover {
    color: #F5DFA0;
    text-decoration: underline;
}
#GhostTextLink[theme="light"] {
    color: #96690A;
}
#GhostTextLink[theme="light"]:hover {
    color: #714F07;
    text-decoration: underline;
}

/* Checkable settings toggle buttons (conflict mode / throttle presets) */
QPushButton[theme="dark"]:checkable:checked {
    background-color: rgba(212, 175, 55, 0.16);
    border: 1px solid #D4AF37;
    color: #F0D68A;
}
QPushButton[theme="light"]:checkable:checked {
    background-color: rgba(184, 134, 11, 0.12);
    border: 1px solid #B8860B;
    color: #8B6508;
}

/* Text inputs (wireless connect dialog, future forms) */
QLineEdit {
    border-radius: 9px;
    padding: 8px 12px;
}
QLineEdit[theme="dark"] {
    background-color: #131317;
    border: 1px solid #2D2D39;
    color: #F2F2F7;
    selection-background-color: #D4AF37;
    selection-color: #14140E;
}
QLineEdit[theme="dark"]:focus {
    border-color: #D4AF37;
}
QLineEdit[theme="light"] {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    color: #1C1C1E;
    selection-background-color: #B8860B;
    selection-color: #FFFFFF;
}
QLineEdit[theme="light"]:focus {
    border-color: #B8860B;
}

/* Scroll areas (settings / history pages) */
QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}

/* Tabs (wireless connect dialog) */
QTabWidget::pane {
    border-radius: 12px;
    top: -1px;
}
QTabWidget::pane[theme="dark"] {
    border: 1px solid #23232A;
    background-color: #131317;
}
QTabWidget::pane[theme="light"] {
    border: 1px solid #E5E5EA;
    background-color: #FFFFFF;
}
QTabBar::tab {
    background-color: transparent;
    padding: 8px 16px;
    border: none;
    font-weight: 600;
}
QTabBar::tab[theme="dark"] {
    color: #9C9CA3;
}
QTabBar::tab[theme="dark"]:selected {
    color: #D4AF37;
    border-bottom: 2px solid #D4AF37;
}
QTabBar::tab[theme="dark"]:hover:!selected {
    color: #E4E4E7;
}
QTabBar::tab[theme="light"] {
    color: #8E8E93;
}
QTabBar::tab[theme="light"]:selected {
    color: #B8860B;
    border-bottom: 2px solid #B8860B;
}
QTabBar::tab[theme="light"]:hover:!selected {
    color: #1C1C1E;
}
"""
