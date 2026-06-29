"""Unit tests for geometry calculations in utils/geometry.py."""

import pytest
from models.entities import Landmark
from utils.geometry import (
    compute_distance,
    compute_hand_scale,
    compute_normalized_distance,
    map_coordinate,
)


def test_compute_distance_2d() -> None:
    """Validates 2D Euclidean distance calculation."""
    pt1 = Landmark(x=0.0, y=0.0, z=0.0)
    pt2 = Landmark(x=3.0, y=4.0, z=0.0)
    assert compute_distance(pt1, pt2, use_3d=False) == 5.0

    # Test extreme boundaries
    pt_zero = Landmark(x=0.0, y=0.0, z=0.0)
    pt_one = Landmark(x=1.0, y=1.0, z=1.0)
    # distance is sqrt(1 + 1) = sqrt(2) approx 1.41421356
    assert compute_distance(pt_zero, pt_one, use_3d=False) == pytest.approx(1.41421356)


def test_compute_distance_3d() -> None:
    """Validates 3D Euclidean distance calculation."""
    pt1 = Landmark(x=0.0, y=0.0, z=0.0)
    pt2 = Landmark(x=1.0, y=2.0, z=2.0)
    assert compute_distance(pt1, pt2, use_3d=True) == 3.0


def test_compute_hand_scale() -> None:
    """Validates hand scale computation using landmark distances."""
    # Build list of 21 landmarks
    landmarks = [Landmark(x=0.0, y=0.0, z=0.0) for _ in range(21)]
    # Set wrist (0) and middle MCP (9)
    landmarks[0] = Landmark(x=10.0, y=20.0, z=0.0)
    landmarks[9] = Landmark(x=13.0, y=24.0, z=0.0)

    # distance is sqrt(3^2 + 4^2) = 5.0
    assert compute_hand_scale(landmarks) == 5.0

    # Test failure/boundary case (less than 21 landmarks)
    assert compute_hand_scale([]) == 1.0
    assert compute_hand_scale(landmarks[:5]) == 1.0

    # Test zero scale fallback
    landmarks[9] = Landmark(x=10.0, y=20.0, z=0.0)
    assert compute_hand_scale(landmarks) == 1.0


def test_compute_normalized_distance() -> None:
    """Validates distance normalization against hand reference scale."""
    pt1 = Landmark(x=0.0, y=0.0, z=0.0)
    pt2 = Landmark(x=3.0, y=4.0, z=0.0)

    # 5.0 / 10.0 = 0.5
    assert compute_normalized_distance(pt1, pt2, 10.0) == 0.5

    # Zero scale protection
    assert compute_normalized_distance(pt1, pt2, 0.0) == 0.0
    assert compute_normalized_distance(pt1, pt2, -1.0) == 0.0


def test_map_coordinate() -> None:
    """Validates coordinate mapping and clamping behaviors."""
    # Standard mapping: map 0.5 from [0.0, 1.0] to [0.0, 100.0] -> 50.0
    assert map_coordinate(0.5, 0.0, 1.0, 0.0, 100.0) == 50.0

    # Clamping below range
    assert map_coordinate(-0.1, 0.0, 1.0, 0.0, 100.0) == 0.0

    # Clamping above range
    assert map_coordinate(1.5, 0.0, 1.0, 0.0, 100.0) == 100.0

    # Division by zero protection (in_min == in_max)
    assert map_coordinate(5.0, 1.0, 1.0, 10.0, 20.0) == 10.0
