"""Headless test runner for the Virtual AI Mouse project.

This script sets up path routing and triggers the pytest suite.
"""

import sys
import pytest


def run() -> None:
    """Executes the test suite under the tests/ directory."""
    print("Initializing Virtual AI Mouse test runner...")
    # Ensure current working directory is in sys.path
    if "." not in sys.path:
        sys.path.insert(0, ".")

    exit_code = pytest.main(["-v", "tests/"])
    sys.exit(exit_code)


if __name__ == "__main__":
    run()
