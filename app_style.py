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
QMainWindow[theme="dark"], QDialog[theme="dark"] {
    background-color: #0C0C0E;
    color: #F2F2F7;
}
QMainWindow[theme="light"], QDialog[theme="light"] {
    background-color: #F2F2F7;
    color: #1C1C1E;
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

QLabel[theme="dark"] {
    color: #F2F2F7;
}
QLabel[theme="light"] {
    color: #1C1C1E;
}

QCheckBox {
    spacing: 8px;
    font-size: 13px;
    font-weight: 500;
}
QCheckBox[theme="dark"] {
    color: #F2F2F7;
}
QCheckBox[theme="light"] {
    color: #1C1C1E;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 5px;
}
QCheckBox::indicator[theme="dark"] {
    background-color: #1B1B22;
    border: 1px solid #333342;
}
QCheckBox::indicator[theme="dark"]:checked {
    background-color: #D4AF37;
    border: 1px solid #E5C158;
}
QCheckBox::indicator[theme="light"] {
    background-color: #FFFFFF;
    border: 1px solid #D1D1D6;
}
QCheckBox::indicator[theme="light"]:checked {
    background-color: #B8860B;
    border: 1px solid #96690A;
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

#PercentBadge {
    font-family: "Segoe UI Variable Display", "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 12px;
}
#PercentBadge[theme="dark"] {
    background-color: rgba(212, 175, 55, 0.15);
    border: 1px solid rgba(212, 175, 55, 0.35);
    color: #F59E0B;
}
#PercentBadge[theme="light"] {
    background-color: rgba(184, 134, 11, 0.12);
    border: 1px solid rgba(184, 134, 11, 0.30);
    color: #B8860B;
}

#MetricTile {
    border-radius: 10px;
    padding: 8px 12px;
}
#MetricTile[theme="dark"] {
    background-color: #1A1A20;
    border: 1px solid #272730;
}
#MetricTile[theme="light"] {
    background-color: #F2F2F7;
    border: 1px solid #E5E5EA;
}

#MetricTileLabel {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}
#MetricTileLabel[theme="dark"] {
    color: #8E8E93;
}
#MetricTileLabel[theme="light"] {
    color: #6E6E73;
}

#MetricTileValue {
    font-family: "Segoe UI Variable Display", "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
    font-weight: 700;
}
#MetricTileValue[theme="dark"] {
    color: #F4F4F5;
}
#MetricTileValue[theme="light"] {
    color: #1C1C1E;
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

/* Phone Browser & Folder Picker Row Elements */
#BrowserDirBtn {
    background-color: transparent;
    border: none;
    text-align: left;
    font-size: 13px;
    font-weight: 600;
    padding: 4px 6px;
}
#BrowserDirBtn[theme="dark"] {
    color: #F4F4F5;
}
#BrowserDirBtn[theme="dark"]:hover {
    color: #D4AF37;
}
#BrowserDirBtn[theme="light"] {
    color: #18181B;
}
#BrowserDirBtn[theme="light"]:hover {
    color: #B8860B;
}

#BrowserFileLabel {
    font-size: 13px;
    font-weight: 500;
    padding: 4px 6px;
}
#BrowserFileLabel[theme="dark"] {
    color: #E4E4E7;
}
#BrowserFileLabel[theme="light"] {
    color: #27272A;
}

#BrowserChevron {
    font-size: 16px;
    font-weight: bold;
}
#BrowserChevron[theme="dark"] {
    color: #71717A;
}
#BrowserChevron[theme="light"] {
    color: #A1A1AA;
}

#BreadcrumbWrap {
    border-radius: 8px;
    padding: 4px 8px;
}
#BreadcrumbWrap[theme="dark"] {
    background-color: #121217;
    border: 1px solid #23232C;
}
#BreadcrumbWrap[theme="light"] {
    background-color: #F2F2F7;
    border: 1px solid #E5E5EA;
}

#BreadcrumbBtn {
    background-color: transparent;
    border: none;
    font-weight: 600;
    font-size: 12px;
    padding: 2px 4px;
}
#BreadcrumbBtn[theme="dark"] {
    color: #E8C766;
}
#BreadcrumbBtn[theme="dark"]:hover {
    color: #F5DFA0;
    text-decoration: underline;
}
#BreadcrumbBtn[theme="light"] {
    color: #96690A;
}
#BreadcrumbBtn[theme="light"]:hover {
    color: #714F07;
    text-decoration: underline;
}

#BreadcrumbSep {
    font-weight: 700;
    font-size: 12px;
}
#BreadcrumbSep[theme="dark"] {
    color: #71717A;
}
#BreadcrumbSep[theme="light"] {
    color: #A1A1AA;
}

/* Checkable settings toggle buttons (conflict mode / throttle presets) */
QPushButton[theme="dark"]:checked {
    background-color: rgba(212, 175, 55, 0.16);
    border: 1px solid #D4AF37;
    color: #F0D68A;
}
QPushButton[theme="light"]:checked {
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

/* Direction Segmented Bar */
#DirectionSegmentContainer {
    border-radius: 12px;
    padding: 3px;
}
#DirectionSegmentContainer[theme="dark"] {
    background-color: #121216;
    border: 1px solid #23232A;
}
#DirectionSegmentContainer[theme="light"] {
    background-color: #EAEAEE;
    border: 1px solid #DCDCE2;
}

#DirectionSegmentBtn {
    border-radius: 9px;
    padding: 7px 16px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid transparent;
    background-color: transparent;
}
#DirectionSegmentBtn[theme="dark"] {
    color: #9C9CA3;
}
#DirectionSegmentBtn[theme="dark"]:hover {
    color: #F2F2F7;
    background-color: rgba(255, 255, 255, 0.04);
}
#DirectionSegmentBtn[theme="dark"][active="true"] {
    background-color: #1F1F26;
    border: 1px solid rgba(212, 175, 55, 0.4);
    color: #D4AF37;
}
#DirectionSegmentBtn[theme="light"] {
    color: #6E6E76;
}
#DirectionSegmentBtn[theme="light"]:hover {
    color: #1C1C1E;
    background-color: rgba(0, 0, 0, 0.04);
}
#DirectionSegmentBtn[theme="light"][active="true"] {
    background-color: #FFFFFF;
    border: 1px solid rgba(184, 134, 11, 0.35);
    color: #B8860B;
}

#DirectionSwapBtn {
    border-radius: 9px;
    padding: 6px 10px;
    background-color: transparent;
    border: 1px solid transparent;
    font-weight: 700;
    font-size: 14px;
}
#DirectionSwapBtn[theme="dark"] {
    color: #D4AF37;
}
#DirectionSwapBtn[theme="dark"]:hover {
    background-color: rgba(212, 175, 55, 0.15);
    border-color: rgba(212, 175, 55, 0.3);
}
#DirectionSwapBtn[theme="light"] {
    color: #B8860B;
}
#DirectionSwapBtn[theme="light"]:hover {
    background-color: rgba(184, 134, 11, 0.12);
    border-color: rgba(184, 134, 11, 0.25);
}

/* Two-Column Split Layout */
#SplitColumnCard {
    border-radius: 14px;
}
#SplitColumnCard[theme="dark"] {
    background-color: #16161B;
    border: 1px solid #23232C;
}
#SplitColumnCard[theme="light"] {
    background-color: #FFFFFF;
    border: 1px solid #E5E5EA;
}

#ColumnRoleBadge {
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
#ColumnRoleBadge[roleType="source"][theme="dark"] {
    background-color: rgba(212, 175, 55, 0.15);
    border: 1px solid rgba(212, 175, 55, 0.35);
    color: #D4AF37;
}
#ColumnRoleBadge[roleType="source"][theme="light"] {
    background-color: rgba(184, 134, 11, 0.12);
    border: 1px solid rgba(184, 134, 11, 0.30);
    color: #B8860B;
}
#ColumnRoleBadge[roleType="dest"][theme="dark"] {
    background-color: rgba(52, 199, 89, 0.12);
    border: 1px solid rgba(52, 199, 89, 0.35);
    color: #34C759;
}
#ColumnRoleBadge[roleType="dest"][theme="light"] {
    background-color: rgba(36, 138, 61, 0.10);
    border: 1px solid rgba(36, 138, 61, 0.30);
    color: #248A3D;
}

#ColumnHeaderTitle {
    font-family: "Segoe UI Variable Display", "Segoe UI", sans-serif;
    font-weight: 700;
    font-size: 14px;
}
#ColumnHeaderTitle[theme="dark"] {
    color: #FFFFFF;
}
#ColumnHeaderTitle[theme="light"] {
    color: #1C1C1E;
}

/* Staged File Item Card */
#StagedFileItemCard {
    border-radius: 9px;
    border: 1px solid transparent;
}
#StagedFileItemCard[theme="dark"] {
    background-color: #1D1D24;
    border-color: #282834;
}
#StagedFileItemCard[theme="dark"]:hover {
    background-color: #23232C;
    border-color: #383848;
}
#StagedFileItemCard[theme="light"] {
    background-color: #F7F7FA;
    border-color: #E5E5EA;
}
#StagedFileItemCard[theme="light"]:hover {
    background-color: #EFEFF4;
    border-color: #D1D1D6;
}

#StagedFileName {
    font-weight: 600;
    font-size: 12px;
}
#StagedFileName[theme="dark"] {
    color: #F2F2F7;
}
#StagedFileName[theme="light"] {
    color: #1C1C1E;
}

#StagedFileSize {
    font-size: 11px;
    color: #8E8E93;
}

#StagedFileRemoveBtn {
    background-color: transparent;
    border: none;
    border-radius: 6px;
    padding: 3px 6px;
    font-weight: 700;
    font-size: 12px;
    color: #8E8E93;
}
#StagedFileRemoveBtn:hover {
    background-color: rgba(255, 69, 58, 0.18);
    color: #FF453A;
}

#StagingSummaryPill {
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 11px;
    font-weight: 600;
}
#StagingSummaryPill[theme="dark"] {
    background-color: rgba(212, 175, 55, 0.10);
    border: 1px solid rgba(212, 175, 55, 0.25);
    color: #D4AF37;
}
#StagingSummaryPill[theme="light"] {
    background-color: rgba(184, 134, 11, 0.08);
    border: 1px solid rgba(184, 134, 11, 0.20);
    color: #B8860B;
}

/* Destination Folder Quick Chips */
#DestQuickChip {
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 11px;
    font-weight: 600;
}
#DestQuickChip[theme="dark"] {
    background-color: #1F1F26;
    border: 1px solid #2C2C38;
    color: #C7C7CC;
}
#DestQuickChip[theme="dark"]:hover {
    background-color: #272732;
    border-color: #D4AF37;
    color: #F2F2F7;
}
#DestQuickChip[theme="dark"][active="true"] {
    background-color: rgba(212, 175, 55, 0.16);
    border: 1px solid #D4AF37;
    color: #D4AF37;
}
#DestQuickChip[theme="light"] {
    background-color: #F2F2F7;
    border: 1px solid #E1E1E6;
    color: #48484A;
}
#DestQuickChip[theme="light"]:hover {
    background-color: #EAEAEE;
    border-color: #B8860B;
    color: #1C1C1E;
}
#DestQuickChip[theme="light"][active="true"] {
    background-color: rgba(184, 134, 11, 0.12);
    border: 1px solid #B8860B;
    color: #B8860B;
}

/* Mode Segment Buttons (Copy / Move) */
#ModeSegmentBtn {
    border-radius: 9px;
    padding: 8px 16px;
    font-size: 12px;
    font-weight: 600;
}
#ModeSegmentBtn[theme="dark"] {
    background-color: #1B1B22;
    border: 1px solid #2A2A36;
    color: #9C9CA3;
}
#ModeSegmentBtn[theme="dark"]:hover {
    background-color: #242430;
    color: #F2F2F7;
}
#ModeSegmentBtn[theme="dark"]:checked {
    background-color: rgba(212, 175, 55, 0.18);
    border: 1px solid #D4AF37;
    color: #F0D68A;
}
#ModeSegmentBtn[theme="light"] {
    background-color: #F2F2F7;
    border: 1px solid #DCDCE2;
    color: #6E6E76;
}
#ModeSegmentBtn[theme="light"]:hover {
    background-color: #E8E8EE;
    color: #1C1C1E;
}
#ModeSegmentBtn[theme="light"]:checked {
    background-color: rgba(184, 134, 11, 0.12);
    border: 1px solid #B8860B;
    color: #8B6508;
}

/* 4-Stage Stepper for Progress Screen */
#StepperContainer {
    border-radius: 14px;
    padding: 12px 16px;
}
#StepperContainer[theme="dark"] {
    background-color: #16161B;
    border: 1px solid #23232C;
}
#StepperContainer[theme="light"] {
    background-color: #FFFFFF;
    border: 1px solid #E5E5EA;
}

#StepBadge {
    border-radius: 14px;
    font-weight: 700;
    font-size: 11px;
    min-width: 28px;
    max-width: 28px;
    min-height: 28px;
    max-height: 28px;
}
#StepBadge[stepState="pending"][theme="dark"] {
    background-color: #202028;
    border: 1px solid #30303C;
    color: #6E6E76;
}
#StepBadge[stepState="pending"][theme="light"] {
    background-color: #E5E5EA;
    border: 1px solid #D1D1D6;
    color: #8E8E93;
}
#StepBadge[stepState="active"][theme="dark"] {
    background-color: rgba(212, 175, 55, 0.22);
    border: 2px solid #D4AF37;
    color: #D4AF37;
}
#StepBadge[stepState="active"][theme="light"] {
    background-color: rgba(184, 134, 11, 0.18);
    border: 2px solid #B8860B;
    color: #B8860B;
}
#StepBadge[stepState="done"][theme="dark"] {
    background-color: rgba(52, 199, 89, 0.18);
    border: 1px solid #34C759;
    color: #34C759;
}
#StepBadge[stepState="done"][theme="light"] {
    background-color: rgba(36, 138, 61, 0.14);
    border: 1px solid #248A3D;
    color: #248A3D;
}

#StepLabel[stepState="pending"][theme="dark"] {
    color: #6E6E76;
    font-size: 11px;
    font-weight: 600;
}
#StepLabel[stepState="pending"][theme="light"] {
    color: #8E8E93;
    font-size: 11px;
    font-weight: 600;
}
#StepLabel[stepState="active"][theme="dark"] {
    color: #D4AF37;
    font-size: 11px;
    font-weight: 700;
}
#StepLabel[stepState="active"][theme="light"] {
    color: #B8860B;
    font-size: 11px;
    font-weight: 700;
}
#StepLabel[stepState="done"][theme="dark"] {
    color: #34C759;
    font-size: 11px;
    font-weight: 600;
}
#StepLabel[stepState="done"][theme="light"] {
    color: #248A3D;
    font-size: 11px;
    font-weight: 600;
}

#StepConnector[theme="dark"] {
    background-color: #2C2C38;
}
#StepConnector[theme="light"] {
    background-color: #DCDCE2;
}
"""

