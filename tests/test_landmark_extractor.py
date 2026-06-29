"""Unit tests for the LandmarkExtractor class in core/landmark_extractor.py."""

from dataclasses import dataclass
from typing import Optional
from core.landmark_extractor import LandmarkExtractor


@dataclass
class MockNormalizedLandmark:
    """Mock for MediaPipe's NormalizedLandmark."""
    x: float
    y: float
    z: float


@dataclass
class MockCategory:
    """Mock for MediaPipe's Category."""
    category_name: str
    display_name: str = ""


@dataclass
class MockHandLandmarkerResult:
    """Mock for MediaPipe's HandLandmarkerResult."""
    hand_landmarks: list[list[MockNormalizedLandmark]]
    handedness: list[list[MockCategory]]


def test_landmark_extractor_empty_result() -> None:
    """Verifies that LandmarkExtractor returns None when no hands are detected."""
    extractor = LandmarkExtractor()

    # Case 1: None result
    assert extractor.extract(None, 640, 480) is None

    # Case 2: Result with empty hand list
    empty_result = MockHandLandmarkerResult(hand_landmarks=[], handedness=[])
    assert extractor.extract(empty_result, 640, 480) is None


def test_landmark_extractor_valid_result() -> None:
    """Verifies that LandmarkExtractor correctly parses and scales detected landmarks."""
    extractor = LandmarkExtractor()

    # Construct mock landmarks (21 points)
    mock_landmarks = [
        MockNormalizedLandmark(x=i * 0.01, y=i * 0.02, z=i * 0.005)
        for i in range(21)
    ]
    mock_category = MockCategory(category_name="right")
    mock_result = MockHandLandmarkerResult(
        hand_landmarks=[mock_landmarks],
        handedness=[[mock_category]]
    )

    frame_width = 640
    frame_height = 480
    hand = extractor.extract(mock_result, frame_width, frame_height)

    assert hand is not None
    assert hand.handedness == "Right"  # Should be capitalized to "Right"
    assert len(hand.landmarks) == 21

    # Verify first landmark values
    # x = 0.0 * 640 = 0.0
    # y = 0.0 * 480 = 0.0
    # z = 0.0
    assert hand.landmarks[0].x == 0.0
    assert hand.landmarks[0].y == 0.0
    assert hand.landmarks[0].z == 0.0

    # Verify tenth landmark values
    # x = 10 * 0.01 * 640 = 0.1 * 640 = 64.0
    # y = 10 * 0.02 * 480 = 0.2 * 480 = 96.0
    # z = 10 * 0.005 = 0.05
    assert hand.landmarks[10].x == 64.0
    assert hand.landmarks[10].y == 96.0
    assert hand.landmarks[10].z == 0.05

    # Verify bounding box computation
    # min x is 0.0, max x is 20 * 0.01 * 640 = 128.0
    # min y is 0.0, max y is 20 * 0.02 * 480 = 192.0
    assert hand.bbox == (0, 0, 128, 192)
