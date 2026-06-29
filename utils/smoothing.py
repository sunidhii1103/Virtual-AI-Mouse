"""Cursor noise reduction filter for the Virtual AI Mouse system.

This module implements smoothing filters to suppress hand tremors and jitter
during cursor movement without introducing significant latency.
"""

from config.settings import SMOOTHING_ALPHA


class EmaFilter:
    """Applies Exponential Moving Average (EMA) filtering to a 2D position stream.

    Maintains historical state internally to compute smoothed coordinates.
    """

    def __init__(self, alpha: float = SMOOTHING_ALPHA) -> None:
        """Initializes the EMA filter.

        Args:
            alpha: The smoothing coefficient between 0.0 (maximum smoothing,
                high lag) and 1.0 (no smoothing, raw responsiveness).
        """
        self._alpha: float = max(0.0, min(1.0, alpha))
        self._smoothed_x: float | None = None
        self._smoothed_y: float | None = None

    def filter(self, x: float, y: float) -> tuple[float, float]:
        """Filters a coordinate pair (x, y) using Exponential Moving Average.

        Args:
            x: The raw x coordinate.
            y: The raw y coordinate.

        Returns:
            A tuple of (smoothed_x, smoothed_y) as floats.
        """
        if self._smoothed_x is None or self._smoothed_y is None:
            # Initialize filter state to the first observed raw values
            self._smoothed_x = float(x)
            self._smoothed_y = float(y)
        else:
            self._smoothed_x = self._alpha * float(x) + (1.0 - self._alpha) * self._smoothed_x
            self._smoothed_y = self._alpha * float(y) + (1.0 - self._alpha) * self._smoothed_y

        return self._smoothed_x, self._smoothed_y

    def reset(self) -> None:
        """Resets the internal filter state.

        Call this when hand detection is lost to prevent the cursor from
        sliding slowly across the screen when a new hand is detected elsewhere.
        """
        self._smoothed_x = None
        self._smoothed_y = None
