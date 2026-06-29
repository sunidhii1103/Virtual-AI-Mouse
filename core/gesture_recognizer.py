"""Gesture recognition module for the Virtual AI Mouse system.

This module contains the logic to classify finger states and resolve hand gestures
based on coordinate geometry, distances, and configuration settings.
"""

import logging
from typing import Any
from models.entities import Hand, Gesture
from utils.geometry import compute_hand_scale, compute_normalized_distance
import config.settings as cfg

logger = logging.getLogger(__name__)


class GestureRecognizer:
    """Deterministic rule-based gesture classification engine."""

    def __init__(self) -> None:
        """Initializes the GestureRecognizer."""
        pass

    def classify_fingers(self, hand: Hand) -> list[bool]:
        """Classifies each of the five fingers as extended (True) or curled (False).

        Args:
            hand: The Hand entity containing 21 pixel-space landmarks.

        Returns:
            A list of 5 booleans [thumb, index, middle, ring, pinky] representing
            whether each finger is extended.
        """
        landmarks = hand.landmarks
        if len(landmarks) < 21:
            return [False, False, False, False, False]

        # Standard fingers: Tip y < PIP y means finger is extended up
        is_index_up = landmarks[8].y < landmarks[6].y
        is_middle_up = landmarks[12].y < landmarks[10].y
        is_ring_up = landmarks[16].y < landmarks[14].y
        is_pinky_up = landmarks[20].y < landmarks[18].y

        # Thumb: check horizontal extension and distance from index MCP to avoid tucked state false positives
        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]
        index_mcp = landmarks[5]

        # Calculate hand scale for distance thresholding
        scale = compute_hand_scale(landmarks)
        dist_thumb_index_mcp = ((thumb_tip.x - index_mcp.x) ** 2 + (thumb_tip.y - index_mcp.y) ** 2) ** 0.5
        norm_thumb_dist = dist_thumb_index_mcp / scale if scale > 0 else 0.0

        if hand.handedness == "Right":
            is_thumb_up = thumb_tip.x < thumb_ip.x and norm_thumb_dist > cfg.THUMB_EXTENSION_DISTANCE_THRESHOLD
        else:
            is_thumb_up = thumb_tip.x > thumb_ip.x and norm_thumb_dist > cfg.THUMB_EXTENSION_DISTANCE_THRESHOLD

        return [is_thumb_up, is_index_up, is_middle_up, is_ring_up, is_pinky_up]

    def recognize_gesture(self, hand: Hand) -> Gesture:
        """Translates hand joint coordinates into a semantic Gesture entity.

        Args:
            hand: The Hand entity containing pixel-space landmarks and metadata.

        Returns:
            A Gesture entity representing the resolved user action.
        """
        try:
            # 1. Classify the open/closed state of each finger
            finger_states = self.classify_fingers(hand)
            is_thumb, is_index, is_middle, is_ring, is_pinky = finger_states

            # 2. Compute dynamic hand reference scale
            scale = compute_hand_scale(hand.landmarks)

            # 3. Compute joint distances for gesture resolution
            # Left Click / Drag (Thumb-Index pinch distance)
            thumb_index_dist = compute_normalized_distance(
                hand.landmarks[4], hand.landmarks[8], scale
            )

            # Right Click (Index-Middle pinch distance)
            index_middle_dist = compute_normalized_distance(
                hand.landmarks[8], hand.landmarks[12], scale
            )

            # Double Click (Thumb-Index-Middle pinch distance)
            thumb_middle_dist = compute_normalized_distance(
                hand.landmarks[4], hand.landmarks[12], scale
            )

            # 4. Deterministic gesture resolving rules
            # Case A: Double Click pinch (all three tips converge)
            if (
                thumb_index_dist < cfg.DOUBLE_CLICK_DISTANCE_THRESHOLD
                and thumb_middle_dist < cfg.DOUBLE_CLICK_DISTANCE_THRESHOLD
            ):
                return Gesture(label=cfg.GESTURE_CLICK_DOUBLE, confidence=1.0, persistence=1)

            # Case B: Left Click / Drag pinch
            if thumb_index_dist < cfg.LEFT_CLICK_DISTANCE_THRESHOLD:
                # Note: Drag actions can be derived from left click state persistence
                return Gesture(label=cfg.GESTURE_CLICK_LEFT, confidence=1.0, persistence=1)

            # Case C: Right Click pinch (index and middle close, both extended, ring and pinky closed)
            if (
                index_middle_dist < cfg.RIGHT_CLICK_DISTANCE_THRESHOLD
                and is_index
                and is_middle
                and not is_ring
                and not is_pinky
            ):
                return Gesture(label=cfg.GESTURE_CLICK_RIGHT, confidence=1.0, persistence=1)

            # Case D: Scroll Mode (Middle finger up alone)
            if not is_thumb and not is_index and is_middle and not is_ring and not is_pinky:
                return Gesture(label=cfg.GESTURE_SCROLL, confidence=1.0, persistence=1)

            # Case E: Zoom Mode (Index and Middle fingers up and apart)
            if not is_thumb and is_index and is_middle and not is_ring and not is_pinky:
                if index_middle_dist > cfg.ZOOM_START_DISTANCE_THRESHOLD:
                    return Gesture(label=cfg.GESTURE_ZOOM, confidence=1.0, persistence=1)
                else:
                    return Gesture(label=cfg.GESTURE_MOVE, confidence=1.0, persistence=1)

            # Case J: Zoom Pinch or Brightness (Thumb and Index extended, others curled)
            if is_thumb and is_index and not is_middle and not is_ring and not is_pinky:
                # Calculate vectors for angle check to detect L-shape / Pistol gesture
                # Vector A: Index MCP (5) -> Index Tip (8)
                v_index = (
                    hand.landmarks[8].x - hand.landmarks[5].x,
                    hand.landmarks[8].y - hand.landmarks[5].y,
                )
                # Vector B: Thumb MCP (2) -> Thumb Tip (4)
                v_thumb = (
                    hand.landmarks[4].x - hand.landmarks[2].x,
                    hand.landmarks[4].y - hand.landmarks[2].y,
                )

                dot_product = v_index[0] * v_thumb[0] + v_index[1] * v_thumb[1]
                mag_index = (v_index[0] ** 2 + v_index[1] ** 2) ** 0.5
                mag_thumb = (v_thumb[0] ** 2 + v_thumb[1] ** 2) ** 0.5

                if mag_index > 0 and mag_thumb > 0:
                    cos_theta = dot_product / (mag_index * mag_thumb)
                else:
                    cos_theta = 1.0

                # L-shape: Angle roughly 90 degrees
                if abs(cos_theta) <= cfg.BRIGHTNESS_ANGLE_COS_THRESHOLD:
                    return Gesture(label=cfg.GESTURE_BRIGHTNESS, confidence=1.0, persistence=1)
                else:
                    return Gesture(label=cfg.GESTURE_ZOOM_PINCH, confidence=1.0, persistence=1)

            # Case F: Cursor Movement (Only Index finger up)
            if not is_thumb and is_index and not is_middle and not is_ring and not is_pinky:
                return Gesture(label=cfg.GESTURE_MOVE, confidence=1.0, persistence=1)

            # Case G: Slide Navigation (Thumb up or down alone)
            if is_thumb and not is_index and not is_middle and not is_ring and not is_pinky:
                thumb_tip = hand.landmarks[4]
                thumb_mcp = hand.landmarks[2]
                if thumb_tip.y < thumb_mcp.y:
                    return Gesture(label=cfg.GESTURE_SLIDE_NEXT, confidence=1.0, persistence=1)
                else:
                    return Gesture(label=cfg.GESTURE_SLIDE_PREV, confidence=1.0, persistence=1)

            # Case H: Volume Control (Index, Middle, Ring up)
            if not is_thumb and is_index and is_middle and is_ring and not is_pinky:
                return Gesture(label=cfg.GESTURE_VOLUME, confidence=1.0, persistence=1)

            # Case I: Page Navigation (Index, Middle, Ring, Pinky up, thumb tucked)
            if not is_thumb and is_index and is_middle and is_ring and is_pinky:
                return Gesture(label=cfg.GESTURE_PAGE_NAV, confidence=1.0, persistence=1)

            # Default fallback for unmapped states
            logger.debug(
                "Ambiguous finger state observed: %s. Returning GESTURE_NONE.",
                finger_states,
            )
            return Gesture(label=cfg.GESTURE_NONE, confidence=0.0, persistence=1)

        except Exception as e:
            logger.error("Unexpected error in gesture recognition: %s", e)
            return Gesture(label=cfg.GESTURE_NONE, confidence=0.0, persistence=1)
