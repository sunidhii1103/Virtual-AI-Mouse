"""Mouse controller module for the Virtual AI Mouse system.

This module controls OS-level cursor movements and clicks using PyAutoGUI,
incorporating coordinate mapping, exponential smoothing, drag-and-drop state,
and click debouncing.
"""

import logging
import pyautogui
from models.entities import Landmark, Screen
from utils.geometry import map_coordinate
from utils.smoothing import EmaFilter
import config.settings as cfg

logger = logging.getLogger(__name__)

# Configure PyAutoGUI settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.0  # Set to 0.0 to eliminate default delay on actions


class MouseController:
    """Orchestrates screen coordinate mapping, filtering, and PyAutoGUI execution."""

    def __init__(self) -> None:
        """Initializes the MouseController."""
        # Query screen resolution at runtime as required by AGENTS.md
        scr_w, scr_h = pyautogui.size()
        self._screen = Screen(width=scr_w, height=scr_h)
        logger.info(
            "Screen dimensions queried: %dx%d. Fail-safe is ENABLED.",
            self._screen.width,
            self._screen.height,
        )

        self._filter = EmaFilter()
        self._is_dragging: bool = False
        self._click_cooldown_counter: int = 0

    def update_cooldown(self) -> None:
        """Ticks down the click cooldown frame counter."""
        if self._click_cooldown_counter > 0:
            self._click_cooldown_counter -= 1

    def map_and_move_cursor(
        self, landmark: Landmark, frame_width: int, frame_height: int
    ) -> tuple[int, int]:
        """Maps frame coordinates to screen coordinates, applies smoothing, and moves cursor.

        Args:
            landmark: The tracking landmark (e.g., Index Finger Tip).
            frame_width: Width of the webcam frame in pixels.
            frame_height: Height of the webcam frame in pixels.

        Returns:
            A tuple of (screen_x, screen_y) where the cursor was moved.
        """
        try:
            # 1. Define active tracking zone boundaries in frame pixel space
            in_xmin = frame_width * cfg.TRACKING_ZONE_X_MIN
            in_xmax = frame_width * cfg.TRACKING_ZONE_X_MAX
            in_ymin = frame_height * cfg.TRACKING_ZONE_Y_MIN
            in_ymax = frame_height * cfg.TRACKING_ZONE_Y_MAX

            # 2. Map coordinates from camera zone to screen bounds
            mapped_x = map_coordinate(
                landmark.x, in_xmin, in_xmax, 0.0, float(self._screen.width)
            )
            mapped_y = map_coordinate(
                landmark.y, in_ymin, in_ymax, 0.0, float(self._screen.height)
            )

            # 3. Apply Exponential Moving Average filtering to eliminate jitter
            smoothed_x, smoothed_y = self._filter.filter(mapped_x, mapped_y)

            # 4. Perform OS-level cursor move
            screen_x = int(smoothed_x)
            screen_y = int(smoothed_y)
            pyautogui.moveTo(screen_x, screen_y)

            return screen_x, screen_y

        except Exception as e:
            logger.error("Exception occurred while moving cursor: %s", e)
            return 0, 0

    def execute_left_click(self) -> None:
        """Executes a left mouse click if the cooldown has expired."""
        if self._click_cooldown_counter == 0:
            try:
                pyautogui.click()
                self._click_cooldown_counter = cfg.CLICK_COOLDOWN_FRAMES
                logger.debug("Executed Left Click")
            except Exception as e:
                logger.warning("Left click action failed: %s", e)

    def execute_right_click(self) -> None:
        """Executes a right mouse click if the cooldown has expired."""
        if self._click_cooldown_counter == 0:
            try:
                pyautogui.rightClick()
                self._click_cooldown_counter = cfg.CLICK_COOLDOWN_FRAMES
                logger.debug("Executed Right Click")
            except Exception as e:
                logger.warning("Right click action failed: %s", e)

    def execute_double_click(self) -> None:
        """Executes a double mouse click if the cooldown has expired."""
        if self._click_cooldown_counter == 0:
            try:
                pyautogui.doubleClick()
                self._click_cooldown_counter = cfg.CLICK_COOLDOWN_FRAMES
                logger.debug("Executed Double Click")
            except Exception as e:
                logger.warning("Double click action failed: %s", e)

    def handle_drag_state(self, should_drag: bool) -> None:
        """Manages the mouse drag-and-drop state transition.

        Args:
            should_drag: True to engage drag (mouseDown), False to release (mouseUp).
        """
        try:
            if should_drag and not self._is_dragging:
                pyautogui.mouseDown()
                self._is_dragging = True
                logger.info("Drag state: ENGAGED (mouseDown)")
            elif not should_drag and self._is_dragging:
                pyautogui.mouseUp()
                self._is_dragging = False
                logger.info("Drag state: RELEASED (mouseUp)")
        except Exception as e:
            logger.warning("Drag state modification failed: %s", e)

    def reset_filters(self) -> None:
        """Resets the internal smoothing filters (call when hand tracking is lost)."""
        self._filter.reset()
        # Release drag state if active to prevent locking up user input
        if self._is_dragging:
            self.handle_drag_state(should_drag=False)
