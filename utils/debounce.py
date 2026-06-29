"""Gesture state debouncer for the Virtual AI Mouse system.

This module implements a state debouncer that filters out high-frequency noise
and transient false gesture classifications in the tracking loop.
"""

from typing import Generic, TypeVar
from config.settings import DEBOUNCE_PERSISTENCE_FRAMES

T = TypeVar("T")


class StateDebouncer(Generic[T]):
    """Tracks state history to ensure transitions persist before confirming them.

    Useful for preventing flickering between gestures (e.g., transient clicks).
    """

    def __init__(
        self, initial_state: T, threshold: int = DEBOUNCE_PERSISTENCE_FRAMES
    ) -> None:
        """Initializes the StateDebouncer.

        Args:
            initial_state: The starting confirmed state.
            threshold: The number of consecutive frames a new candidate state
                must persist before transitioning.
        """
        self._confirmed_state: T = initial_state
        self._candidate_state: T = initial_state
        self._candidate_count: int = 0
        self._threshold: int = max(1, threshold)

    def update(self, raw_state: T) -> T:
        """Updates the state history with a new observation and returns the debounced state.

        Args:
            raw_state: The raw, un-debounced state observed in the current frame.

        Returns:
            The stabilized state (either the confirmed state or a newly confirmed candidate state).
        """
        if raw_state == self._confirmed_state:
            # The raw state matches the confirmed state; reset candidate tracking.
            self._candidate_state = raw_state
            self._candidate_count = 0
        elif raw_state == self._candidate_state:
            # The raw state matches the candidate state; increment persistence count.
            self._candidate_count += 1
            if self._candidate_count >= self._threshold:
                self._confirmed_state = raw_state
                self._candidate_count = 0
        else:
            # Observed a new candidate state; start tracking persistence.
            self._candidate_state = raw_state
            self._candidate_count = 1

            # Edge case: If threshold is 1, instantly transition
            if self._candidate_count >= self._threshold:
                self._confirmed_state = raw_state
                self._candidate_count = 0

        return self._confirmed_state

    @property
    def confirmed_state(self) -> T:
        """Gets the currently confirmed state."""
        return self._confirmed_state

    def reset(self, state: T) -> None:
        """Resets the debouncer to a specific confirmed state.

        Args:
            state: The state to force-confirm.
        """
        self._confirmed_state = state
        self._candidate_state = state
        self._candidate_count = 0
