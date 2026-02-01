"""
Animation Timing Constants
Centralized timing values for consistent motion design.

Usage:
    from src.utils.animation import TIMING, EASING, HoverDebouncer

    self.after(TIMING.HOVER_DELAY, self._apply_hover_effect)
"""

from dataclasses import dataclass
from typing import Dict, Callable, Optional


@dataclass(frozen=True)
class AnimationTiming:
    """
    Animation duration constants in milliseconds.

    Based on Material Design motion principles:
    - Micro-interactions: 50-150ms
    - Small transitions: 150-300ms
    - Medium transitions: 300-500ms
    - Large/complex: 500ms+
    """

    # Micro-interactions (immediate feedback)
    INSTANT: int = 0
    PRESS: int = 80
    RELEASE: int = 100

    # Hover effects
    HOVER_IN: int = 150
    HOVER_OUT: int = 200

    # Focus transitions
    FOCUS_IN: int = 100
    FOCUS_OUT: int = 150

    # State changes
    STATE_CHANGE: int = 200
    COLOR_SHIFT: int = 150

    # Layout changes
    EXPAND: int = 250
    COLLAPSE: int = 200
    SLIDE: int = 300

    # Feedback
    TOAST_IN: int = 300
    TOAST_OUT: int = 250
    TOAST_DURATION: int = 3000

    # Loading indicators
    SPINNER_CYCLE: int = 1000
    PULSE_CYCLE: int = 1500
    PROGRESS_UPDATE: int = 100

    # Delays
    HOVER_DELAY: int = 50
    TOOLTIP_DELAY: int = 500
    DEBOUNCE: int = 150


@dataclass(frozen=True)
class EasingCurves:
    """
    Easing curve names for reference.

    CustomTkinter doesn't support CSS-style easing directly,
    but these serve as documentation for manual interpolation.
    """

    EASE_IN: str = "ease-in"
    EASE_OUT: str = "ease-out"
    EASE_IN_OUT: str = "ease-in-out"
    LINEAR: str = "linear"
    EASE_OUT_BACK: str = "ease-out-back"
    EASE_OUT_ELASTIC: str = "ease-out-elastic"
    BUTTON_PRESS: str = "ease-out"
    BUTTON_RELEASE: str = "ease-out"
    HOVER: str = "ease-out"
    PANEL_SLIDE: str = "ease-in-out"
    FADE: str = "ease-out"


TIMING = AnimationTiming()
EASING = EasingCurves()


def delayed_call(widget, delay_ms: int, callback: Callable):
    """
    Schedule a callback after delay.

    Args:
        widget: Any tkinter widget (for .after() method)
        delay_ms: Delay in milliseconds
        callback: Function to call

    Returns:
        Timer ID (can be cancelled with widget.after_cancel())
    """
    return widget.after(delay_ms, callback)


def cancel_delayed_call(widget, timer_id: Optional[str]):
    """Cancel a scheduled callback."""
    if timer_id:
        try:
            widget.after_cancel(timer_id)
        except Exception:
            pass


class HoverDebouncer:
    """
    Debounce hover events to prevent flicker on rapid mouse movement.

    Usage:
        self._hover_debouncer = HoverDebouncer(self)

        def _on_enter(self, event):
            self._hover_debouncer.schedule(self._apply_hover)

        def _on_leave(self, event):
            self._hover_debouncer.cancel()
            self._remove_hover()
    """

    def __init__(self, widget, delay: int = TIMING.HOVER_DELAY):
        self._widget = widget
        self._delay = delay
        self._timer_id: Optional[str] = None

    def schedule(self, callback: Callable):
        """Schedule callback after hover delay."""
        self.cancel()
        self._timer_id = self._widget.after(self._delay, callback)

    def cancel(self):
        """Cancel pending callback."""
        if self._timer_id:
            try:
                self._widget.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None


__all__ = [
    "TIMING",
    "EASING",
    "AnimationTiming",
    "EasingCurves",
    "delayed_call",
    "cancel_delayed_call",
    "HoverDebouncer",
]
