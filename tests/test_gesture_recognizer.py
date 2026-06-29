"""Unit tests for the GestureRecognizer rule engine in core/gesture_recognizer.py."""

import pytest
from models.entities import Hand, Landmark
from core.gesture_recognizer import GestureRecognizer
import config.settings as cfg


def create_mock_hand(finger_states: list[bool], handedness: str = "Right") -> Hand:
    """Helper to construct a mock Hand entity with predefined finger extension states.

    finger_states order: [thumb, index, middle, ring, pinky]
    """
    landmarks = [Landmark(x=100.0, y=100.0, z=0.0) for _ in range(21)]
    is_thumb, is_index, is_middle, is_ring, is_pinky = finger_states

    # Wrist
    landmarks[0] = Landmark(x=100.0, y=200.0, z=0.0)
    # Middle MCP (landmark 9) to define hand scale (dist between 0 and 9)
    # Scale = dist( (100, 200), (100, 100) ) = 100.0
    landmarks[9] = Landmark(x=100.0, y=100.0, z=0.0)

    # Index (8, 6)
    if is_index:
        landmarks[8] = Landmark(x=100.0, y=30.0, z=0.0)  # y < 50 (up)
        landmarks[6] = Landmark(x=100.0, y=50.0, z=0.0)
    else:
        landmarks[8] = Landmark(x=100.0, y=70.0, z=0.0)  # y > 50 (down)
        landmarks[6] = Landmark(x=100.0, y=50.0, z=0.0)

    # Middle (12, 10)
    if is_middle:
        landmarks[12] = Landmark(x=120.0, y=30.0, z=0.0)
        landmarks[10] = Landmark(x=120.0, y=50.0, z=0.0)
    else:
        landmarks[12] = Landmark(x=120.0, y=70.0, z=0.0)
        landmarks[10] = Landmark(x=120.0, y=50.0, z=0.0)

    # Ring (16, 14)
    if is_ring:
        landmarks[16] = Landmark(x=140.0, y=30.0, z=0.0)
        landmarks[14] = Landmark(x=140.0, y=50.0, z=0.0)
    else:
        landmarks[16] = Landmark(x=140.0, y=70.0, z=0.0)
        landmarks[14] = Landmark(x=140.0, y=50.0, z=0.0)

    # Pinky (20, 18)
    if is_pinky:
        landmarks[20] = Landmark(x=160.0, y=30.0, z=0.0)
        landmarks[18] = Landmark(x=160.0, y=50.0, z=0.0)
    else:
        landmarks[20] = Landmark(x=160.0, y=70.0, z=0.0)
        landmarks[18] = Landmark(x=160.0, y=50.0, z=0.0)

    # Thumb: 4 (tip), 3 (IP)
    # Right hand: open if tip.x < IP.x. Left hand: open if tip.x > IP.x.
    landmarks[3] = Landmark(x=80.0, y=120.0, z=0.0)
    landmarks[2] = Landmark(x=90.0, y=130.0, z=0.0)  # MCP
    if is_thumb:
        if handedness == "Right":
            landmarks[4] = Landmark(x=50.0, y=120.0, z=0.0)  # x < 80
        else:
            landmarks[4] = Landmark(x=140.0, y=120.0, z=0.0)  # x > 80
    else:
        if handedness == "Right":
            landmarks[4] = Landmark(x=90.0, y=120.0, z=0.0)  # x > 80
        else:
            landmarks[4] = Landmark(x=70.0, y=120.0, z=0.0)  # x < 80

    return Hand(landmarks=landmarks, handedness=handedness, bbox=(0, 0, 200, 200))


def test_classify_fingers() -> None:
    """Validates the finger classification flags for open/closed fingers."""
    recognizer = GestureRecognizer()

    # Case 1: All fingers up
    hand_all_up = create_mock_hand([True, True, True, True, True], handedness="Right")
    assert recognizer.classify_fingers(hand_all_up) == [True, True, True, True, True]

    # Case 2: Only Index up
    hand_index_up = create_mock_hand([False, True, False, False, False], handedness="Right")
    assert recognizer.classify_fingers(hand_index_up) == [False, True, False, False, False]

    # Case 3: Only Thumb up (Left hand)
    hand_thumb_left = create_mock_hand([True, False, False, False, False], handedness="Left")
    assert recognizer.classify_fingers(hand_thumb_left) == [True, False, False, False, False]


def test_recognize_move_gesture() -> None:
    """Validates GESTURE_MOVE resolution when only index finger is up."""
    recognizer = GestureRecognizer()
    hand = create_mock_hand([False, True, False, False, False])
    gesture = recognizer.recognize_gesture(hand)
    assert gesture.label == cfg.GESTURE_MOVE


def test_recognize_left_click_gesture() -> None:
    """Validates GESTURE_CLICK_LEFT resolution when thumb and index tip converge (pinch)."""
    recognizer = GestureRecognizer()
    hand = create_mock_hand([True, True, False, False, False])
    # Place thumb tip (4) and index tip (8) close together
    # Hand scale is 100.0. A normalized distance < 0.25 (say 15.0 pixels) triggers left click.
    hand.landmarks[4] = Landmark(x=90.0, y=40.0, z=0.0)
    hand.landmarks[8] = Landmark(x=100.0, y=40.0, z=0.0)

    gesture = recognizer.recognize_gesture(hand)
    assert gesture.label == cfg.GESTURE_CLICK_LEFT


def test_recognize_right_click_gesture() -> None:
    """Validates GESTURE_CLICK_RIGHT resolution index-middle tip pinch."""
    recognizer = GestureRecognizer()
    hand = create_mock_hand([False, True, True, False, False])
    # Index tip (8) and Middle tip (12) close together (say 10 pixels dist)
    hand.landmarks[8] = Landmark(x=100.0, y=30.0, z=0.0)
    hand.landmarks[12] = Landmark(x=105.0, y=30.0, z=0.0)

    gesture = recognizer.recognize_gesture(hand)
    assert gesture.label == cfg.GESTURE_CLICK_RIGHT


def test_recognize_scroll_gesture() -> None:
    """Validates GESTURE_SCROLL resolution when only middle finger is up."""
    recognizer = GestureRecognizer()
    hand = create_mock_hand([False, False, True, False, False])
    gesture = recognizer.recognize_gesture(hand)
    assert gesture.label == cfg.GESTURE_SCROLL


def test_recognize_volume_control_gesture() -> None:
    """Validates GESTURE_VOLUME when index, middle, ring are up."""
    recognizer = GestureRecognizer()
    hand = create_mock_hand([False, True, True, True, False])
    gesture = recognizer.recognize_gesture(hand)
    assert gesture.label == cfg.GESTURE_VOLUME


def test_recognize_page_nav_gesture() -> None:
    """Validates GESTURE_PAGE_NAV resolution when index, middle, ring, and pinky are up, thumb tucked."""
    recognizer = GestureRecognizer()
    hand = create_mock_hand([False, True, True, True, True])
    gesture = recognizer.recognize_gesture(hand)
    assert gesture.label == cfg.GESTURE_PAGE_NAV


def test_recognize_zoom_pinch_gesture() -> None:
    """Validates GESTURE_ZOOM_PINCH resolution when thumb and index are up and not pinching."""
    recognizer = GestureRecognizer()
    hand = create_mock_hand([True, True, False, False, False])
    # Place thumb tip (4) and index tip (8) far apart and not at 90 degrees
    hand.landmarks[4] = Landmark(x=60.0, y=50.0, z=0.0)
    hand.landmarks[8] = Landmark(x=100.0, y=30.0, z=0.0)

    gesture = recognizer.recognize_gesture(hand)
    assert gesture.label == cfg.GESTURE_ZOOM_PINCH


def test_recognize_brightness_gesture() -> None:
    """Validates GESTURE_BRIGHTNESS resolution when thumb and index are extended at roughly 90 degrees."""
    recognizer = GestureRecognizer()
    hand = create_mock_hand([True, True, False, False, False])
    # Place thumb tip (4) and index tip (8) far apart at roughly 90 degrees
    # Index vector: MCP (100, 100) -> Tip (100, 30) => (0, -70)
    # Thumb vector: MCP (90, 130) -> Tip (30, 120) => (-60, -10)
    hand.landmarks[4] = Landmark(x=30.0, y=120.0, z=0.0)
    hand.landmarks[8] = Landmark(x=100.0, y=30.0, z=0.0)

    gesture = recognizer.recognize_gesture(hand)
    assert gesture.label == cfg.GESTURE_BRIGHTNESS
