"""Presentation controller module for the Virtual AI Mouse system.

This module maps navigation gestures to OS keyboard press events to control
presentation slides, incorporating state debouncing and cooldown frames.
"""

import logging
import pyautogui
from utils.debounce import StateDebouncer
import config.settings as cfg

logger = logging.getLogger(__name__)


class PresentationController:
    """Manages presentation slide navigation with debouncing and cooldown safety."""

    def __init__(self) -> None:
        """Initializes the PresentationController."""
        # Initialize debouncer for slide actions
        self._debouncer = StateDebouncer(
            initial_state=cfg.GESTURE_NONE, threshold=cfg.DEBOUNCE_PERSISTENCE_FRAMES
        )
        self._cooldown_counter: int = 0

    def update_cooldown(self) -> None:
        """Ticks down the slide navigation cooldown frame counter."""
        if self._cooldown_counter > 0:
            self._cooldown_counter -= 1

    def handle_gesture(self, gesture_label: str) -> None:
        """Processes the recognized gesture and dispatches keyboard events.

        Args:
            gesture_label: The raw gesture label observed in the current frame.
        """
        self.update_cooldown()

        # Update the debouncer state with the raw gesture label
        debounced_gesture = self._debouncer.update(gesture_label)

        if self._cooldown_counter == 0:
            try:
                if debounced_gesture == cfg.GESTURE_SLIDE_NEXT:
                    pyautogui.press(cfg.KEY_SLIDE_NEXT)
                    self._cooldown_counter = cfg.SLIDE_NAV_COOLDOWN_FRAMES
                    logger.info("Presentation Action: Next Slide ('%s')", cfg.KEY_SLIDE_NEXT)
                    # Reset debouncer to prevent continuous trigger
                    self._debouncer.reset(cfg.GESTURE_NONE)
                elif debounced_gesture == cfg.GESTURE_SLIDE_PREV:
                    pyautogui.press(cfg.KEY_SLIDE_PREV)
                    self._cooldown_counter = cfg.SLIDE_NAV_COOLDOWN_FRAMES
                    logger.info("Presentation Action: Previous Slide ('%s')", cfg.KEY_SLIDE_PREV)
                    # Reset debouncer to prevent continuous trigger
                    self._debouncer.reset(cfg.GESTURE_NONE)
            except Exception as e:
                logger.error("Failed to press slide navigation key: %s", e)
