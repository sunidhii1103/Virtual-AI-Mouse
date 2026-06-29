"""Overlay renderer module for the Virtual AI Mouse system.

This module draws the hand skeleton, tracking zone bounding box, and HUD elements
(FPS, active gesture, telemetry) onto OpenCV frame matrices.
"""

import logging
import cv2
import numpy as np
from models.entities import Hand
import config.settings as cfg

logger = logging.getLogger(__name__)

# Standard connections between the 21 MediaPipe hand landmarks
HAND_CONNECTIONS = [
    # Thumb
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    # Index
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    # Middle
    (9, 10),
    (10, 11),
    (11, 12),
    # Ring
    (13, 14),
    (14, 15),
    (15, 16),
    # Pinky
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    # Palm knuckles
    (5, 9),
    (9, 13),
    (13, 17),
]


class OverlayRenderer:
    """Draws visual feedback and performance HUDs onto video frames."""

    def __init__(self) -> None:
        """Initializes the OverlayRenderer."""
        pass

    def draw_hud(
        self,
        frame: np.ndarray,
        fps: float,
        gesture_label: str,
        system_status: str | None = None,
    ) -> None:
        """Renders the HUD panel containing system telemetry on the top-left corner.

        Args:
            frame: The image matrix to draw on.
            fps: Current real-time frame rate.
            gesture_label: The name of the active gesture.
            system_status: Optional string indicating system status warnings.
        """
        # Draw background panel for text readability (semi-transparent dark box)
        panel_h, panel_w = 100, 260
        sub_img = frame[10 : 10 + panel_h, 10 : 10 + panel_w]
        black_rect = np.zeros_like(sub_img)
        # Blend the black box
        cv2.addWeighted(sub_img, 0.4, black_rect, 0.6, 0, sub_img)
        frame[10 : 10 + panel_h, 10 : 10 + panel_w] = sub_img

        # Render HUD metrics
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.5
        thickness = 1
        text_color = (255, 255, 255)  # White

        cv2.putText(
            frame,
            f"FPS: {fps:.1f}",
            (20, 30),
            font,
            font_scale,
            text_color,
            thickness,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            f"Gesture: {gesture_label}",
            (20, 55),
            font,
            font_scale,
            text_color,
            thickness,
            cv2.LINE_AA,
        )

        status_text = system_status if system_status else "System OK"
        status_color = (0, 255, 0) if "OK" in status_text else (0, 165, 255)  # Green vs Orange
        cv2.putText(
            frame,
            f"Status: {status_text}",
            (20, 80),
            font,
            font_scale,
            status_color,
            thickness,
            cv2.LINE_AA,
        )

    def draw_tracking_zone(self, frame: np.ndarray, is_inside: bool = True) -> None:
        """Draws the active tracking zone boundary box on the frame.

        Args:
            frame: The image matrix to draw on.
            is_inside: Whether the tracked landmark is inside the tracking zone.
        """
        h, w = frame.shape[:2]
        xmin = int(w * cfg.TRACKING_ZONE_X_MIN)
        xmax = int(w * cfg.TRACKING_ZONE_X_MAX)
        ymin = int(h * cfg.TRACKING_ZONE_Y_MIN)
        ymax = int(h * cfg.TRACKING_ZONE_Y_MAX)

        # Draw box: green if user is inside active zone, red if out of bounds
        box_color = (0, 255, 0) if is_inside else (0, 0, 255)
        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), box_color, 2)

        # Add label above bounding box
        font = cv2.FONT_HERSHEY_SIMPLEX
        label = "INTERACTION ZONE" if is_inside else "OUT OF BOUNDS!"
        cv2.putText(frame, label, (xmin, ymin - 10), font, 0.5, box_color, 1, cv2.LINE_AA)

    def draw_hand_skeleton(self, frame: np.ndarray, hand: Hand) -> None:
        """Draws the hand joints and connections on the frame.

        Args:
            frame: The image matrix to draw on.
            hand: The structured Hand entity containing pixel-space coordinates.
        """
        landmarks = hand.landmarks
        if not landmarks:
            return

        # 1. Draw connections (skeleton lines)
        for connection in HAND_CONNECTIONS:
            idx1, idx2 = connection
            if idx1 < len(landmarks) and idx2 < len(landmarks):
                pt1 = (int(landmarks[idx1].x), int(landmarks[idx1].y))
                pt2 = (int(landmarks[idx2].x), int(landmarks[idx2].y))
                # Soft blue line for skeletal connections
                cv2.line(frame, pt1, pt2, (255, 180, 100), 2, cv2.LINE_AA)

        # 2. Draw joints (circle landmarks)
        for idx, lm in enumerate(landmarks):
            pt = (int(lm.x), int(lm.y))
            # Highlight index fingertip (8) and thumb tip (4) for pinch feedback
            if idx in [4, 8]:
                cv2.circle(frame, pt, 6, (0, 0, 255), -1, cv2.LINE_AA)  # Red filled circle
            elif idx == 12:
                cv2.circle(frame, pt, 5, (0, 255, 255), -1, cv2.LINE_AA)  # Yellow
            else:
                cv2.circle(frame, pt, 4, (0, 255, 0), -1, cv2.LINE_AA)  # Green filled circle
