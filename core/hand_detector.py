"""Hand detector module for the Virtual AI Mouse system.

This module wraps Google's MediaPipe Hands task to process video frames
and detect hands, handling color space conversions and error boundaries.
"""

import logging
import time
import urllib.request
import os
from typing import Any
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

from config.settings import (
    MP_MAX_NUM_HANDS,
    MP_MIN_DETECTION_CONFIDENCE,
    MP_MIN_TRACKING_CONFIDENCE,
    MP_MODEL_ASSET_PATH,
)

logger = logging.getLogger(__name__)

# Monkey-patch mp.Image to support create_from_numpy_image if it does not exist
if not hasattr(mp.Image, "create_from_numpy_image"):
    @staticmethod
    def create_from_numpy_image(rgb_frame: np.ndarray) -> mp.Image:
        """Creates an mp.Image wrapper from a numpy RGB frame.

        Args:
            rgb_frame: Input video frame in RGB format.

        Returns:
            An mp.Image wrapper.
        """
        return mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
    mp.Image.create_from_numpy_image = create_from_numpy_image


class HandDetector:
    """Wrapper class for MediaPipe Hand Tracking framework."""

    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_hands: int = MP_MAX_NUM_HANDS,
        min_detection_confidence: float = MP_MIN_DETECTION_CONFIDENCE,
        min_tracking_confidence: float = MP_MIN_TRACKING_CONFIDENCE,
    ) -> None:
        """Initializes the MediaPipe Hands wrapper.

        Args:
            static_image_mode: If True, detects hands on static images rather than streaming video.
            max_num_hands: Maximum number of hands to detect.
            min_detection_confidence: Minimum confidence score for hand detection.
            min_tracking_confidence: Minimum confidence score for hand tracking.
        """
        # Ensure model file exists at local path location, download if missing
        model_path = MP_MODEL_ASSET_PATH
        if not os.path.exists(model_path):
            print("Downloading MediaPipe hand landmarker model...")
            logger.info("Downloading MediaPipe hand landmarker model to %s...", model_path)
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            try:
                urllib.request.urlretrieve(url, model_path)
            except Exception as e:
                logger.error("Error downloading hand landmarker model: %s", e)
                raise e

        # Leverage RunningMode.VIDEO or RunningMode.LIVE_STREAM for temporal caching across video frames to enable tracking caching
        running_mode = (
            vision.RunningMode.IMAGE
            if static_image_mode
            else vision.RunningMode.VIDEO
        )
        if running_mode in (vision.RunningMode.VIDEO, vision.RunningMode.LIVE_STREAM):
            logger.info("MediaPipe HandLandmarker tracking mode successfully verified: %s", running_mode.name)
        else:
            logger.warning("MediaPipe HandLandmarker initialized in static image mode: %s", running_mode.name)

        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=running_mode,
            num_hands=max_num_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_hand_presence_confidence=min_tracking_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        try:
            self._hands = vision.HandLandmarker.create_from_options(options)
        except Exception as e:
            logger.critical("Failed to initialize MediaPipe HandLandmarker: %s", e)
            raise RuntimeError(f"Failed to initialize MediaPipe HandLandmarker: {e}") from e

        self._running_mode = running_mode
        self._last_timestamp_ms: int = 0

    def detect_hands(self, bgr_frame: np.ndarray) -> Any:
        """Processes a BGR OpenCV frame and returns raw MediaPipe detection results.

        Converts the BGR frame to RGB color space before passing it to MediaPipe.

        Args:
            bgr_frame: Input video frame in BGR format.

        Returns:
            The raw HandLandmarkerResult output containing hand_landmarks and handedness.
            Returns None if processing fails or raises an exception.
        """
        try:
            # MediaPipe requires RGB images, but OpenCV reads frames in BGR
            rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image.create_from_numpy_image(rgb_frame)

            if self._running_mode == vision.RunningMode.VIDEO:
                # Calculate monotonic timestamp in milliseconds
                timestamp_ms = int(time.perf_counter() * 1000)
                if timestamp_ms <= self._last_timestamp_ms:
                    timestamp_ms = self._last_timestamp_ms + 1
                self._last_timestamp_ms = timestamp_ms
                results = self._hands.detect_for_video(mp_image, timestamp_ms)
            else:
                results = self._hands.detect(mp_image)
            return results
        except Exception as e:
            logger.error("Exception during MediaPipe hands processing: %s", e)
            return None

    def close(self) -> None:
        """Closes the MediaPipe Hands resources."""
        try:
            self._hands.close()
        except Exception as e:
            logger.warning("Error closing MediaPipe hands instance: %s", e)
