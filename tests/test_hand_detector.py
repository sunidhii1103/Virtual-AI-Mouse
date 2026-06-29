"""Unit tests for the HandDetector class in core/hand_detector.py."""

import numpy as np
from core.hand_detector import HandDetector


def test_hand_detector_initialization() -> None:
    """Verifies that the HandDetector initializes correctly and closes without error."""
    detector = HandDetector(static_image_mode=True)
    assert detector._hands is not None
    detector.close()


def test_hand_detector_detect_hands() -> None:
    """Verifies that detect_hands processes a frame and returns expected result format."""
    detector = HandDetector(static_image_mode=True)
    try:
        # Create a black frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = detector.detect_hands(frame)
        assert result is not None
        assert hasattr(result, "hand_landmarks")
        assert len(result.hand_landmarks) == 0
    finally:
        detector.close()
