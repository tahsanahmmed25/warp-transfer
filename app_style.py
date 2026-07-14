# Design System & Styling definitions for Warp Transfer (PyQt6 QSS)
# v2 — production visual pass: refined elevation, consistent radii/spacing,
# gradient accents, clearer state feedback, unified icon-badge system.

APP_STYLE_DARK = """
/* Global Styles */
QMainWindow {
    background-color: #0C0C0E;
}

QWidget {
    color: #F2F2F7;
    font-family: "Segoe UI Variable Text", "Segoe UI", "Inter", -apple-system, sans-serif;
    font-size: 13px;
}

QToolTip {
    background-color: #1D1D24;
    color: #F2F2F7;
    border: 1px solid #2B2B35;
    border-radius: 6px;
    padding: 6px 10px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #121214;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #2D2D34;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background-color: #D4AF37;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Frameless Window Header / TitleBar */
#TitleBar {
    background-color: #121214;
    border-bottom: 1px solid #1F1F24;
}
#TitleLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", "Inter", sans-serif;
    font-weight: 600;
    font-size: 14px;
    color: #F2F2F7;
    letter-spacing: 0.2px;
}
#LogoBadge {
    background-color: rgba(212, 175, 55, 0.14);
    border: 1px solid rgba(212, 175, 55, 0.35);
    border-radius: 9px;
}

/* Titlebar window control buttons */
#TitleBarButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
}
#TitleBarButton:hover {
    background-color: #23232B;
}
#TitleBarButton:pressed {
    background-color: #1A1A20;
}
#CloseButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
}
#CloseButton:hover {
    background-color: #E5484D;
}
#CloseButton:pressed {
    background-color: #C23A3E;
}

/* Navigation & Progress Dots */
#DotActive {
    background-color: #D4AF37;
    border-radius: 4px;
}
#DotInactive {
    background-color: #2D2D34;
    border-radius: 4px;
}

/* Cards & Containers */
#CardContainer {
    background-color: #16161A;
    border: 1px solid #23232A;
    border-radius: 16px;
}

#InnerCard {
    background-color: #1B1B21;
    border: 1px solid #29293380;
    border-radius: 14px;
}

/* OnboardingWizard live connection-status banner */
#StatusBannerWarning {
    background-color: rgba(224, 122, 63, 0.12);
    border: 1px solid rgba(224, 122, 63, 0.35);
    border-radius: 10px;
    color: #E0A15E;
    padding: 10px 14px;
    font-size: 13px;
}
#StatusBannerNeutral {
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid #29293380;
    border-radius: 10px;
    color: #9C9CA6;
    padding: 10px 14px;
    font-size: 13px;
}

#IconBadge {
    background-color: rgba(212, 175, 55, 0.12);
    border: 1px solid rgba(212, 175, 55, 0.28);
    border-radius: 11px;
}

/* Labels */
#HeaderLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", "Inter", sans-serif;
    font-weight: 700;
    font-size: 24px;
    color: #FFFFFF;
}

#SubHeaderLabel {
    color: #A9A9B2;
    font-size: 14px;
    line-height: 20px;
}

#StepTitleLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-weight: 700;
    font-size: 18px;
    color: #FFFFFF;
}

#StatusLabel {
    font-weight: 600;
    color: #D4AF37;
}

#SuccessStatusLabel {
    font-weight: 600;
    font-size: 11px;
    color: #34C759;
}

#StepNumberLabel {
    background-color: #23232A;
    border: 1px solid #35353F;
    color: #D4AF37;
    border-radius: 12px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
}

#PathLabel {
    color: #9C9CA3;
    font-size: 12px;
}

#DestHeaderLabel {
    font-size: 11px;
    color: #7C7C84;
    font-weight: 600;
    letter-spacing: 0.4px;
}

#DragDropTitleLabel {
    font-weight: 600;
    font-size: 13px;
    color: #E4E4E7;
}

#DragDropSubtextLabel {
    color: #8E8E93;
    font-size: 11px;
}

#DeviceTitleLabel {
    font-weight: 700;
    font-size: 15px;
    color: #FFFFFF;
}

#TransferDetailLabel {
    font-size: 13px;
    font-weight: 600;
    color: #E4E4E7;
}

#TransferFileLabel {
    color: #8E8E93;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #1E1E24;
    border: 1px solid #2D2D39;
    color: #F2F2F7;
    border-radius: 10px;
    padding: 9px 18px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #26262E;
    border-color: #3D3D4E;
}
QPushButton:pressed {
    background-color: #141418;
}

QPushButton:disabled {
    background-color: #121214;
    border-color: #1A1A1E;
    color: #48484A;
}

/* Primary Call to Action Button */
#PrimaryButton {
    background-color: #D4AF37;
    border: 1px solid #E5C158;
    color: #14140E;
    padding: 9px 22px;
}
#PrimaryButton:hover {
    background-color: #E0BC4C;
    border-color: #F3D279;
}
#PrimaryButton:pressed {
    background-color: #B89327;
}
#PrimaryButton:disabled {
    background-color: #3A3423;
    border-color: #3A3423;
    color: #706A54;
}

/* Secondary/Danger Button */
#DangerButton {
    background-color: #2A1415;
    border: 1px solid #4D2022;
    color: #FF6961;
}
#DangerButton:hover {
    background-color: #3D1C1E;
    border-color: #6E2D30;
}
#DangerButton:pressed {
    background-color: #1F0D0E;
}
#DangerButton:disabled {
    background-color: #1A1112;
    border-color: #2A1A1B;
    color: #6B4344;
}

/* Quick Action Buttons (Large layout) */
#QuickActionButton {
    background-color: #17171B;
    border: 1px solid #24242C;
    border-radius: 14px;
    padding: 16px;
    text-align: left;
}
#QuickActionButton:hover {
    border-color: #D4AF37;
    background-color: #1C1C21;
}
#QuickActionButton:pressed {
    background-color: #131316;
}
#QuickActionButtonTitle {
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: #FFFFFF;
}
#QuickActionButtonDesc {
    color: #8E8E93;
    font-size: 11px;
}

/* Drag and Drop Zone */
#DropZone {
    background-color: #131317;
    border: 2px dashed #2C2C36;
    border-radius: 16px;
}
#DropZone[dragActive="true"] {
    border-color: #D4AF37;
    background-color: #1E1B10;
}

/* Progress bar */
QProgressBar {
    background-color: #1A1A1F;
    border: 1px solid #26262E;
    border-radius: 7px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #B8860B, stop:1 #E5C158);
    border-radius: 6px;
}

/* Secondary outline button used for links/downloads */
#LinkButton {
    background-color: transparent;
    border: 1px solid #2D2D39;
    color: #D4AF37;
    font-weight: 600;
}
#LinkButton:hover {
    background-color: #1C1C21;
    border-color: #D4AF37;
}

/* Checkable settings toggle buttons (conflict mode / throttle presets) */
QPushButton:checkable:checked {
    background-color: rgba(212, 175, 55, 0.16);
    border: 1px solid #D4AF37;
    color: #F0D68A;
}

/* Text inputs (wireless connect dialog, future forms) */
QLineEdit {
    background-color: #131317;
    border: 1px solid #2D2D39;
    border-radius: 9px;
    padding: 8px 12px;
    color: #F2F2F7;
    selection-background-color: #D4AF37;
    selection-color: #14140E;
}
QLineEdit:focus {
    border-color: #D4AF37;
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
    border: 1px solid #23232A;
    border-radius: 12px;
    background-color: #131317;
    top: -1px;
}
QTabBar::tab {
    background-color: transparent;
    color: #9C9CA3;
    padding: 8px 16px;
    border: none;
    font-weight: 600;
}
QTabBar::tab:selected {
    color: #D4AF37;
    border-bottom: 2px solid #D4AF37;
}
QTabBar::tab:hover:!selected {
    color: #E4E4E7;
}
"""

APP_STYLE_LIGHT = """
/* Global Styles */
QMainWindow {
    background-color: #F2F2F7;
}

QWidget {
    color: #1C1C1E;
    font-family: "Segoe UI Variable Text", "Segoe UI", "Inter", -apple-system, sans-serif;
    font-size: 13px;
}

QToolTip {
    background-color: #FFFFFF;
    color: #1C1C1E;
    border: 1px solid #E5E5EA;
    border-radius: 6px;
    padding: 6px 10px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background-color: #E5E5EA;
    width: 8px;
    margin: 0px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #C7C7CC;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::handle:vertical:hover {
    background-color: #B8860B;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Frameless Window Header / TitleBar */
#TitleBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E5EA;
}
#TitleLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", "Inter", sans-serif;
    font-weight: 600;
    font-size: 14px;
    color: #1C1C1E;
    letter-spacing: 0.2px;
}
#LogoBadge {
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
#TitleBarButton:hover {
    background-color: #EDEDF2;
}
#TitleBarButton:pressed {
    background-color: #E2E2E8;
}
#CloseButton {
    background-color: transparent;
    border: none;
    border-radius: 6px;
}
#CloseButton:hover {
    background-color: #FF3B30;
}
#CloseButton:pressed {
    background-color: #D93227;
}

/* Navigation & Progress Dots */
#DotActive {
    background-color: #B8860B;
    border-radius: 4px;
}
#DotInactive {
    background-color: #D1D1D6;
    border-radius: 4px;
}

/* Cards & Containers */
#CardContainer {
    background-color: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 16px;
}

#InnerCard {
    background-color: #FFFFFF;
    border: 1px solid #E9E9EE;
    border-radius: 14px;
}

/* OnboardingWizard live connection-status banner */
#StatusBannerWarning {
    background-color: rgba(196, 106, 41, 0.10);
    border: 1px solid rgba(196, 106, 41, 0.30);
    border-radius: 10px;
    color: #A85A24;
    padding: 10px 14px;
    font-size: 13px;
}
#StatusBannerNeutral {
    background-color: rgba(0, 0, 0, 0.03);
    border: 1px solid #E9E9EE;
    border-radius: 10px;
    color: #6E6E76;
    padding: 10px 14px;
    font-size: 13px;
}

#IconBadge {
    background-color: rgba(184, 134, 11, 0.10);
    border: 1px solid rgba(184, 134, 11, 0.25);
    border-radius: 11px;
}

/* Labels */
#HeaderLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", "Inter", sans-serif;
    font-weight: 700;
    font-size: 24px;
    color: #1C1C1E;
}

#SubHeaderLabel {
    color: #58585C;
    font-size: 14px;
    line-height: 20px;
}

#StepTitleLabel {
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-weight: 700;
    font-size: 18px;
    color: #1C1C1E;
}

#StatusLabel {
    font-weight: 600;
    color: #B8860B;
}

#SuccessStatusLabel {
    font-weight: 600;
    font-size: 11px;
    color: #248A3D;
}

#StepNumberLabel {
    background-color: #F2F2F7;
    border: 1px solid #E1E1E6;
    color: #B8860B;
    border-radius: 12px;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 1px;
}

#PathLabel {
    color: #86868B;
    font-size: 12px;
}

#DestHeaderLabel {
    font-size: 11px;
    color: #86868B;
    font-weight: 600;
    letter-spacing: 0.4px;
}

#DragDropTitleLabel {
    font-weight: 600;
    font-size: 13px;
    color: #1C1C1E;
}

#DragDropSubtextLabel {
    color: #8E8E93;
    font-size: 11px;
}

#DeviceTitleLabel {
    font-weight: 700;
    font-size: 15px;
    color: #1C1C1E;
}

#TransferDetailLabel {
    font-size: 13px;
    font-weight: 600;
    color: #1C1C1E;
}

#TransferFileLabel {
    color: #8E8E93;
    font-size: 12px;
}

/* Buttons */
QPushButton {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    color: #1C1C1E;
    border-radius: 10px;
    padding: 9px 18px;
    font-weight: 600;
}
QPushButton:hover {
    background-color: #F5F5F7;
    border-color: #C7C7CC;
}
QPushButton:pressed {
    background-color: #E5E5EA;
}

QPushButton:disabled {
    background-color: #F2F2F7;
    border-color: #E5E5EA;
    color: #AEAEB2;
}

/* Primary Call to Action Button */
#PrimaryButton {
    background-color: #B8860B;
    border: 1px solid #A0720A;
    color: #FFFFFF;
    padding: 9px 22px;
}
#PrimaryButton:hover {
    background-color: #CD9A13;
    border-color: #B8860B;
}
#PrimaryButton:pressed {
    background-color: #8B6508;
}
#PrimaryButton:disabled {
    background-color: #EAE0C8;
    border-color: #EAE0C8;
    color: #B8AD8E;
}

/* Secondary/Danger Button */
#DangerButton {
    background-color: #FDF2F2;
    border: 1px solid #F5C2C2;
    color: #E0342A;
}
#DangerButton:hover {
    background-color: #FBE5E5;
    border-color: #F1A5A5;
}
#DangerButton:pressed {
    background-color: #F7D0D0;
}
#DangerButton:disabled {
    background-color: #FAF3F3;
    border-color: #F0DCDC;
    color: #D9A8A8;
}

/* Quick Action Buttons (Large layout) */
#QuickActionButton {
    background-color: #FFFFFF;
    border: 1px solid #E5E5EA;
    border-radius: 14px;
    padding: 16px;
    text-align: left;
}
#QuickActionButton:hover {
    border-color: #B8860B;
    background-color: #FCFAF4;
}
#QuickActionButton:pressed {
    background-color: #F5F2E8;
}
#QuickActionButtonTitle {
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-weight: 700;
    font-size: 14px;
    color: #1C1C1E;
}
#QuickActionButtonDesc {
    color: #8E8E93;
    font-size: 11px;
}

/* Drag and Drop Zone */
#DropZone {
    background-color: #F8F8FA;
    border: 2px dashed #D1D1D6;
    border-radius: 16px;
}
#DropZone[dragActive="true"] {
    border-color: #B8860B;
    background-color: #FBF6E9;
}

/* Progress bar */
QProgressBar {
    background-color: #E9E9EE;
    border: 1px solid #DBDBE1;
    border-radius: 7px;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #B8860B, stop:1 #D9A82B);
    border-radius: 6px;
}

/* Secondary outline button used for links/downloads */
#LinkButton {
    background-color: transparent;
    border: 1px solid #D1D1D6;
    color: #B8860B;
    font-weight: 600;
}
#LinkButton:hover {
    background-color: #FCFAF4;
    border-color: #B8860B;
}

/* Checkable settings toggle buttons (conflict mode / throttle presets) */
QPushButton:checkable:checked {
    background-color: rgba(184, 134, 11, 0.12);
    border: 1px solid #B8860B;
    color: #8B6508;
}

/* Text inputs (wireless connect dialog, future forms) */
QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
    border-radius: 9px;
    padding: 8px 12px;
    color: #1C1C1E;
    selection-background-color: #B8860B;
    selection-color: #FFFFFF;
}
QLineEdit:focus {
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
    border: 1px solid #E5E5EA;
    border-radius: 12px;
    background-color: #FFFFFF;
    top: -1px;
}
QTabBar::tab {
    background-color: transparent;
    color: #8E8E93;
    padding: 8px 16px;
    border: none;
    font-weight: 600;
}
QTabBar::tab:selected {
    color: #B8860B;
    border-bottom: 2px solid #B8860B;
}
QTabBar::tab:hover:!selected {
    color: #1C1C1E;
}
"""
