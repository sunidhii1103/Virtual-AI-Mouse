"""Latency benchmarking and profiling utility for the Virtual AI Mouse system.

This module provides a context manager to track and log elapsed execution time
of core pipeline operations, checking against the performance frame budget.
"""

import time
import logging
from typing import Iterator
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PipelineProfiler:
    """Measures, aggregates, and logs latency metrics for execution blocks."""

    def __init__(self, warning_threshold_ms: float = 66.0) -> None:
        """Initializes the PipelineProfiler.

        Args:
            warning_threshold_ms: Maximum budget before emitting a warning log.
        """
        self._threshold = warning_threshold_ms
        self._metrics: dict[str, float] = {}

    @contextmanager
    def profile(self, block_name: str) -> Iterator[None]:
        """Context manager to measure the latency of a code block.

        Args:
            block_name: A descriptive label for the block being timed.
        """
        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            self._metrics[block_name] = elapsed_ms
            logger.debug("Block [%s] took %.2f ms", block_name, elapsed_ms)

    def log_and_verify_budget(self) -> None:
        """Summates active metrics and checks them against the performance budget."""
        total_latency = sum(self._metrics.values())

        # Format metric breakdowns for debug level
        breakdown = ", ".join(f"{name}={val:.2f}ms" for name, val in self._metrics.items())
        logger.debug("Latency breakdown: %s (Total=%.2fms)", breakdown, total_latency)

        if total_latency > self._threshold:
            logger.warning(
                "Latency budget breached! Total pipeline duration: %.2f ms (Threshold: %.2f ms)",
                total_latency,
                self._threshold,
            )

    def clear(self) -> None:
        """Resets the accumulated metrics dictionary for the next frame iteration."""
        self._metrics.clear()
