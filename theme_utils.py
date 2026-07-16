# Shared theme-tagging helper for Warp Transfer.
#
# Extracted from MainWindow._tag_theme() (main.py) so ConflictDialog and
# DevicePickerDialog can correctly tag themselves too. Previously ONLY
# MainWindow's own widget tree ever got tagged with the current theme --
# both dialogs build and exec() themselves in one static ask(...) call, so
# MainWindow never had a handle to reach in and tag them before they show.
# This was a known, self-documented gap in _tag_theme()'s own docstring
# (see dev_notes.md, flagged since Session N+4, never fixed until now).
#
# Extracting to a shared function (rather than duplicating the loop in three
# places, or having the dialogs reach into a MainWindow instance) keeps the
# exact same proven-correct behavior everywhere it's used -- including the
# setUpdatesEnabled(False)/True freeze that Session N+8 added to prevent
# torn-frame repaints during the retag loop. A dialog is just as capable of
# showing a torn frame mid-retag as MainWindow is, so it gets the same
# protection, not a simplified copy.

from PyQt6.QtWidgets import QWidget


def tag_theme_recursive(root: QWidget, is_dark: bool):
    """Recursively set the `theme` dynamic QSS property (+ unpolish/polish)
    on `root` and every descendant widget. Qt QSS attribute selectors like
    [theme="dark"] are not inherited from an ancestor -- each widget needs
    the property set on itself for its own rules to match.

    Freezes repaints on `root` for the duration of the retag loop (same
    reasoning as MainWindow._tag_theme(), see dev_notes.md Session N+8):
    without this, Qt can flush a partial repaint mid-loop, showing some
    widgets already retagged and others still on the old theme.
    """
    theme_str = "dark" if is_dark else "light"
    targets = [root] + root.findChildren(QWidget)
    root.setUpdatesEnabled(False)
    try:
        for w in targets:
            w.setProperty("theme", theme_str)
            w.style().unpolish(w)
            w.style().polish(w)
    finally:
        root.setUpdatesEnabled(True)
    root.update()
