"""Configuration settings and constants for the Virtual AI Mouse system.

This module houses all calibration thresholds, hardware defaults, window settings,
gesture definitions, and application constraints. It serves as the single source
of truth for constants, ensuring no magic numbers exist in execution logic.
"""

# Camera Settings
CAMERA_DEVICE_INDEX: int = 0
CAMERA_FRAME_WIDTH: int = 640
CAMERA_FRAME_HEIGHT: int = 480
CAMERA_FPS: int = 30

# UI Display Settings
WINDOW_NAME: str = "Virtual AI Mouse - Gesture Control"
FONT_FACE: int = 0  # cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE: float = 0.6
FONT_THICKNESS: int = 2
COLOR_GREEN: tuple[int, int, int] = (0, 255, 0)
COLOR_RED: tuple[int, int, int] = (0, 0, 255)
COLOR_BLUE: tuple[int, int, int] = (255, 0, 0)
COLOR_YELLOW: tuple[int, int, int] = (0, 255, 255)
COLOR_WHITE: tuple[int, int, int] = (255, 255, 255)

# Coordinate Mapping and Smoothing
# Normalised tracking region inside the camera frame to map to the full screen.
# Hand coordinates outside this box are capped to the boundaries.
TRACKING_ZONE_X_MIN: float = 0.2
TRACKING_ZONE_X_MAX: float = 0.8
TRACKING_ZONE_Y_MIN: float = 0.2
TRACKING_ZONE_Y_MAX: float = 0.8
PAGE_NAV_THRESHOLD: float = 25.0
MOVE_THRESHOLD: float = 5.0

# Cursor Smoothing Factor (alpha for Exponential Moving Average)
# 1.0 = no smoothing (raw coordinates), 0.01 = heavy smoothing (slow but no jitter)
SMOOTHING_ALPHA: float = 0.40

# Gesture Names
GESTURE_MOVE: str = "MOUSE_MOVE"
GESTURE_CLICK_LEFT: str = "CLICK_LEFT"
GESTURE_CLICK_RIGHT: str = "CLICK_RIGHT"
GESTURE_CLICK_DOUBLE: str = "CLICK_DOUBLE"
GESTURE_DRAG: str = "MOUSE_DRAG"
GESTURE_SCROLL: str = "MOUSE_SCROLL"
GESTURE_ZOOM: str = "MOUSE_ZOOM"
GESTURE_SLIDE_NEXT: str = "SLIDE_NEXT"
GESTURE_SLIDE_PREV: str = "SLIDE_PREV"
GESTURE_VOLUME: str = "VOLUME_CONTROL"
GESTURE_BRIGHTNESS: str = "BRIGHTNESS_CONTROL"
GESTURE_PAGE_NAV: str = "PAGE_NAV"
GESTURE_ZOOM_PINCH: str = "ZOOM_PINCH"
GESTURE_NONE: str = "NONE"

# Distance Thresholds (normalised by hand reference scale)
# Standard hand reference scale is the Euclidean distance between Wrist (landmark 0)
# and Middle Finger MCP joint (landmark 9).
LEFT_CLICK_DISTANCE_THRESHOLD: float = 0.25
RIGHT_CLICK_DISTANCE_THRESHOLD: float = 0.30
DOUBLE_CLICK_DISTANCE_THRESHOLD: float = 0.30
DRAG_START_DISTANCE_THRESHOLD: float = 0.22
DRAG_RELEASE_DISTANCE_THRESHOLD: float = 0.35
ZOOM_START_DISTANCE_THRESHOLD: float = 0.40
BRIGHTNESS_ANGLE_COS_THRESHOLD: float = 0.57
ZOOM_IN_MULTIPLIER: float = 1.25
ZOOM_OUT_MULTIPLIER: float = 0.75
THUMB_EXTENSION_DISTANCE_THRESHOLD: float = 0.35

# Debouncing and Timing (in frames)
DEBOUNCE_PERSISTENCE_FRAMES: int = 3
CLICK_COOLDOWN_FRAMES: int = 10
SLIDE_NAV_COOLDOWN_FRAMES: int = 15
PAGE_NAV_COOLDOWN_FRAMES: int = 15
VOLUME_COOLDOWN_FRAMES: int = 5

# MediaPipe Hands Settings
MP_MAX_NUM_HANDS: int = 1
MP_MIN_DETECTION_CONFIDENCE: float = 0.7
MP_MIN_TRACKING_CONFIDENCE: float = 0.7
MP_MODEL_ASSET_PATH: str = "hand_landmarker.task"

# Slide Navigation Key Bindings
KEY_SLIDE_NEXT: str = "right"
KEY_SLIDE_PREV: str = "left"

# Exit Key Code (ASCII value for ESC key)
EXIT_KEY_CODE: int = 27

# Debug Settings
IS_DEBUG_MODE: bool = False

