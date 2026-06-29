"""Camera module for the Virtual AI Mouse system.

This module encapsulates OpenCV VideoCapture functionality to manage the lifecycle
of the webcam capture device, acquire frames, and apply preprocessing such as horizontal flipping.
"""

import logging
import cv2
import numpy as np
from typing import Self
from config.settings import (
    CAMERA_DEVICE_INDEX,
    CAMERA_FRAME_WIDTH,
    CAMERA_FRAME_HEIGHT,
    CAMERA_FPS,
)

logger = logging.getLogger(__name__)


class CameraError(Exception):
    """Custom exception raised for camera errors."""
    pass


class CameraModule:
    """Manages the OpenCV VideoCapture device lifecycle and frame ingestion.

    Supports context manager protocol for clean setup and tear down of resources.
    """

    def __init__(
        self,
        device_index: int = CAMERA_DEVICE_INDEX,
        width: int = CAMERA_FRAME_WIDTH,
        height: int = CAMERA_FRAME_HEIGHT,
        fps: int = CAMERA_FPS,
    ) -> None:
        """Initializes the camera module.

        Args:
            device_index: The index of the camera hardware device.
            width: Configured camera frame width.
            height: Configured camera frame height.
            fps: Configured camera frame rate.
        """
        self._device_index: int = device_index
        self._width: int = width
        self._height: int = height
        self._fps: int = fps
        self._cap: cv2.VideoCapture | None = None

    def __enter__(self) -> Self:
        """Enters the context manager block, opening the camera.

        Returns:
            The CameraModule instance.

        Raises:
            CameraError: If the video capture device cannot be opened.
        """
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exits the context manager block, releasing the camera resources."""
        self.release()

    def open(self) -> None:
        """Opens the webcam and configures properties.

        Raises:
            CameraError: If the device fails to open.
        """
        logger.info("Initializing camera device index: %d", self._device_index)
        try:
            self._cap = cv2.VideoCapture(self._device_index)
            if not self._cap.isOpened():
                raise CameraError(
                    f"Failed to open video capture device at index {self._device_index}"
                )

            # Set resolution and FPS (explicitly clamped to exactly 640x480)
            clamped_width = min(self._width, 640)
            clamped_height = min(self._height, 480)
            self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, clamped_width)
            self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, clamped_height)
            self._cap.set(cv2.CAP_PROP_FPS, self._fps)

            # Read back configuration values to verify
            actual_w = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            actual_h = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            logger.info("Camera initialized. Frame resolution set to %dx%d", actual_w, actual_h)

        except Exception as e:
            if not isinstance(e, CameraError):
                raise CameraError(f"Unexpected camera initialization failure: {e}") from e
            raise

    def read_frame(self) -> np.ndarray | None:
        """Captures a single frame from the camera stream, mirrors it, and returns it.

        Returns:
            The mirrored BGR frame as a numpy array, or None if reading failed.

        Raises:
            CameraError: If camera is not initialized.
        """
        if self._cap is None or not self._cap.isOpened():
            raise CameraError("Camera is not open. Call open() or enter context first.")

        try:
            ret, frame = self._cap.read()
            if not ret or frame is None:
                logger.warning("Dropped frame or read failure from webcam.")
                return None

            # Present mirrored frame to user so movement is intuitive (mirror image)
            mirrored_frame = cv2.flip(frame, 1)
            return mirrored_frame

        except Exception as e:
            logger.error("Error reading frame from capture device: %s", e)
            return None

    def release(self) -> None:
        """Releases the camera hardware capture device."""
        if self._cap is not None:
            logger.info("Releasing camera device index: %d", self._device_index)
            self._cap.release()
            self._cap = None
