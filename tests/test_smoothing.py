"""Unit tests for the Exponential Moving Average filter in utils/smoothing.py."""

import pytest
from utils.smoothing import EmaFilter


def test_ema_filter_initialization() -> None:
    """Validates the first frame outputs match the raw inputs exactly."""
    filter_instance = EmaFilter(alpha=0.2)
    # First frame should return the inputs exactly
    smoothed_x, smoothed_y = filter_instance.filter(100.0, 200.0)
    assert smoothed_x == 100.0
    assert smoothed_y == 200.0


def test_ema_filter_smoothing_math() -> None:
    """Validates math calculation: S_t = alpha * Y_t + (1 - alpha) * S_{t-1}."""
    alpha = 0.2
    filter_instance = EmaFilter(alpha=alpha)

    # Frame 1
    filter_instance.filter(10.0, 20.0)

    # Frame 2: input is 20.0, 30.0
    # Expected x: 0.2 * 20.0 + 0.8 * 10.0 = 4.0 + 8.0 = 12.0
    # Expected y: 0.2 * 30.0 + 0.8 * 20.0 = 6.0 + 16.0 = 22.0
    smoothed_x, smoothed_y = filter_instance.filter(20.0, 30.0)
    assert smoothed_x == pytest.approx(12.0)
    assert smoothed_y == pytest.approx(22.0)


def test_ema_filter_reset() -> None:
    """Validates resetting the filter clears historical state and starts fresh."""
    filter_instance = EmaFilter(alpha=0.5)

    # Frame 1
    filter_instance.filter(10.0, 10.0)
    # Frame 2
    filter_instance.filter(20.0, 20.0)

    # Reset
    filter_instance.reset()
    assert filter_instance._smoothed_x is None
    assert filter_instance._smoothed_y is None

    # Next filter should act as first frame (return input exactly)
    smoothed_x, smoothed_y = filter_instance.filter(50.0, 50.0)
    assert smoothed_x == 50.0
    assert smoothed_y == 50.0


def test_ema_filter_tremor_simulation() -> None:
    """Validates that high-frequency noise/jitter is smoothed out over time."""
    # Low alpha (0.1) should smooth heavily
    filter_instance = EmaFilter(alpha=0.1)

    # First frame establishes base position
    filter_instance.filter(100.0, 100.0)

    # Tremor alternating between 98 and 102
    results = []
    for i in range(10):
        val = 102.0 if i % 2 == 0 else 98.0
        sx, _ = filter_instance.filter(val, val)
        results.append(sx)

    # Over 10 frames of 102/98 tremors, the smoothed output must remain stable
    # and stay very close to the center 100.0, showing jitter reduction
    for rx in results[5:]:
        assert 99.0 <= rx <= 101.0


def test_ema_filter_boundary_alpha() -> None:
    """Validates that alpha values outside [0, 1] are clamped safely."""
    f_under = EmaFilter(alpha=-0.5)
    assert f_under._alpha == 0.0

    f_over = EmaFilter(alpha=1.5)
    assert f_over._alpha == 1.0
