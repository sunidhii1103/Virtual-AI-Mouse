"""Data model entities for the Virtual AI Mouse system.

This module defines the type-safe, dataclass-based representations of various
components in the gesture processing pipeline, such as hand landmarks, hands,
gestures, cursors, and the screen coordinates.
"""

from dataclasses import dataclass


@dataclass
class Landmark:
    """Represents a single hand landmark in pixel space.

    Attributes:
        x: The horizontal coordinate in pixel space.
        y: The vertical coordinate in pixel space.
        z: The depth coordinate, relative to the wrist (MediaPipe standard).
    """
    x: float
    y: float
    z: float


@dataclass
class Hand:
    """Represents a detected hand with its landmarks and metadata.

    Attributes:
        landmarks: A list of 21 landmark coordinates representing finger joints.
        handedness: A string indicating whether the hand is 'Left' or 'Right'.
        bbox: A bounding box around the hand represented as (xmin, ymin, xmax, ymax) in pixels.
    """
    landmarks: list[Landmark]
    handedness: str
    bbox: tuple[int, int, int, int]


@dataclass
class Gesture:
    """Represents a recognized hand gesture.

    Attributes:
        label: The semantic label of the gesture (e.g., 'MOUSE_MOVE', 'CLICK_LEFT').
        confidence: The confidence score of the recognition, between 0.0 and 1.0.
        persistence: The number of consecutive frames this gesture has been sustained.
    """
    label: str
    confidence: float
    persistence: int


@dataclass
class Cursor:
    """Represents the state of the mouse cursor.

    Attributes:
        x: The horizontal pixel position of the cursor on the screen.
        y: The vertical pixel position of the cursor on the screen.
        is_drag_active: A flag indicating if drag-and-drop mode is currently engaged.
    """
    x: int
    y: int
    is_drag_active: bool = False


@dataclass
class Screen:
    """Represents the dimensions of the display screen.

    Attributes:
        width: The width of the screen in pixels.
        height: The height of the screen in pixels.
    """
    width: int
    height: int
