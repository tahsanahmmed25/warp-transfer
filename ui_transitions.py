# Shared page-transition helper for Warp Transfer (PyQt6)
#
# Extracted from OnboardingWizard._fade_to_index (onboarding_wizard.py) so
# MainWindow's QStackedWidget transitions (dashboard <-> onboarding,
# settings/history <-> dashboard, transfer progress -> result) get the same
# 220ms cross-fade instead of a hard setCurrentIndex()/setCurrentWidget()
# cut. See localsend_parity_plan.md Phase 2.

from PyQt6.QtWidgets import QGraphicsOpacityEffect
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve


def fade_to_page(stacked_widget, target, duration=220, on_finished=None):
    """Cross-fade `stacked_widget` to `target` (either a QWidget already in
    the stack, or an integer index).

    Returns the QPropertyAnimation. IMPORTANT: the caller must keep a
    reference to the returned animation (e.g. store it as an attribute like
    `self._page_fade_anim`) or PyQt will garbage-collect the Python wrapper
    mid-flight and the fade will silently never complete -- this is the
    same gotcha the original OnboardingWizard._fade_to_index avoided by
    storing `self._fade_anim`.

    If `target` is already the current widget, this is a no-op and returns
    None -- skips restarting a fade for a redundant same-page call (e.g.
    a poll-triggered refresh that doesn't actually change pages).

    `on_finished`, if given, runs after the fade completes (e.g. clearing
    a "transition in progress" flag) -- the helper doesn't manage any such
    state itself, that's the call site's responsibility.
    """
    current = stacked_widget.currentWidget()
    if isinstance(target, int):
        target_widget = stacked_widget.widget(target)
    else:
        target_widget = target

    if target_widget is current:
        if on_finished:
            on_finished()
        return None

    if isinstance(target, int):
        stacked_widget.setCurrentIndex(target)
    else:
        stacked_widget.setCurrentWidget(target)

    incoming = stacked_widget.currentWidget()

    effect = QGraphicsOpacityEffect(incoming)
    incoming.setGraphicsEffect(effect)

    anim = QPropertyAnimation(effect, b"opacity")
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)

    def _cleanup():
        incoming.setGraphicsEffect(None)
        if on_finished:
            on_finished()

    anim.finished.connect(_cleanup)
    anim.start()

    return anim
