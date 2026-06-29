"""Geometry utilities for the Virtual AI Mouse system.

This module provides pure functions for geometric operations on Landmarks,
including distance calculations, hand reference scaling, and linear mapping
(coordinate interpolation).
"""

import math
from models.entities import Landmark


def compute_distance(point_a: Landmark, point_b: Landmark, use_3d: bool = False) -> float:
    """Computes the Euclidean distance between two hand landmarks.

    Args:
        point_a: First landmark.
        point_b: Second landmark.
        use_3d: If True, computes distance in 3D space (x, y, z).
            Otherwise, computes in 2D space (x, y).

    Returns:
        The Euclidean distance as a float.
    """
    dx = point_a.x - point_b.x
    dy = point_a.y - point_b.y
    if use_3d:
        dz = point_a.z - point_b.z
        return math.sqrt(dx * dx + dy * dy + dz * dz)
    return math.sqrt(dx * dx + dy * dy)


def compute_hand_scale(landmarks: list[Landmark]) -> float:
    """Computes a stable reference scale of the hand.

    Uses the Euclidean distance between the Wrist (landmark 0) and the
    Middle Finger MCP joint (landmark 9) as a stable reference.

    Args:
        landmarks: A list of 21 landmarks representing the hand.

    Returns:
        The reference hand scale as a float. Returns 1.0 if joint index is
        out of bounds or distance is zero to prevent DivisionByZero downstream.
    """
    if len(landmarks) <= 9:
        return 1.0
    wrist = landmarks[0]
    middle_mcp = landmarks[9]
    scale = compute_distance(wrist, middle_mcp, use_3d=False)
    return scale if scale > 0.0 else 1.0


def compute_normalized_distance(
    point_a: Landmark, point_b: Landmark, reference_scale: float
) -> float:
    """Computes the distance between two points normalized by a hand reference scale.

    Args:
        point_a: First landmark.
        point_b: Second landmark.
        reference_scale: The hand reference scale (wrist to middle MCP distance).

    Returns:
        The normalized distance. Returns 0.0 if the reference_scale is <= 0.0
        to prevent division by zero.
    """
    if reference_scale <= 0.0:
        return 0.0
    absolute_distance = compute_distance(point_a, point_b, use_3d=False)
    return absolute_distance / reference_scale


def map_coordinate(
    value: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    """Maps a value from an input range to an output range, with clamping.

    Args:
        value: The raw input coordinate to map.
        in_min: The start of the input range.
        in_max: The end of the input range.
        out_min: The start of the output range.
        out_max: The end of the output range.

    Returns:
        The mapped and clamped coordinate value as a float.
    """
    if in_max == in_min:
        return out_min

    mapped = out_min + ((value - in_min) / (in_max - in_min)) * (out_max - out_min)

    # Clamp outputs within output boundaries
    low = min(out_min, out_max)
    high = max(out_min, out_max)
    return max(low, min(mapped, high))
