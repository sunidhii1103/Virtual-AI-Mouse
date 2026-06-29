"""Landmark extraction module for the Virtual AI Mouse system.

This module processes raw MediaPipe Hand landmarks, converts them from normalized
coordinates to pixel-space coordinates, calculates hand bounding boxes, and instantiates
the type-safe entities defined in models.entities.
"""

import logging
from typing import Any
from models.entities import Hand, Landmark

logger = logging.getLogger(__name__)


class LandmarkExtractor:
    """Converts MediaPipe detection results into structured Hand and Landmark entities."""

    def extract(self, raw_result: Any, frame_width: int, frame_height: int) -> Hand | None:
        """Extracts hand entity from raw MediaPipe results.

        Processes the first detected hand, converting all 21 landmarks into pixel coordinates
        and calculating the bounding box.

        Args:
            raw_result: The raw output object from MediaPipe HandLandmarker.
            frame_width: Width of the input frame in pixels.
            frame_height: Height of the input frame in pixels.

        Returns:
            A Hand entity containing pixel-space landmarks, handedness, and a bounding box,
            or None if no hand was detected or extraction failed.
        """
        if not raw_result or not getattr(raw_result, "hand_landmarks", None):
            return None

        try:
            # We track a single hand (the first one detected) as configured in settings
            hand_landmarks = raw_result.hand_landmarks[0]

            # Extract handedness label ('Left' or 'Right')
            handedness_label = "Unknown"
            if getattr(raw_result, "handedness", None) and len(raw_result.handedness) > 0:
                cat = raw_result.handedness[0][0]
                label_str = getattr(cat, "category_name", None) or getattr(cat, "display_name", "Unknown")
                handedness_label = label_str.capitalize()

            landmarks: list[Landmark] = []
            x_pixels: list[float] = []
            y_pixels: list[float] = []

            for lm in hand_landmarks:
                # Convert normalized [0, 1] coordinates to absolute pixel coordinates
                px_x = lm.x * frame_width
                px_y = lm.y * frame_height
                # Depth z is relative to wrist; we keep it normalized as output by MediaPipe
                px_z = lm.z

                landmarks.append(Landmark(x=px_x, y=px_y, z=px_z))
                x_pixels.append(px_x)
                y_pixels.append(px_y)

            # Compute bounding box coordinates (xmin, ymin, xmax, ymax) in pixel space
            xmin = max(0, int(min(x_pixels)))
            ymin = max(0, int(min(y_pixels)))
            xmax = min(frame_width, int(max(x_pixels)))
            ymax = min(frame_height, int(max(y_pixels)))

            bbox = (xmin, ymin, xmax, ymax)

            return Hand(
                landmarks=landmarks,
                handedness=handedness_label,
                bbox=bbox
            )

        except Exception as e:
            logger.error("Error extracting landmarks from MediaPipe results: %s", e)
            return None
