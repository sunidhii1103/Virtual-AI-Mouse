# AGENTS.md — Development Rules for AI Coding Assistants

## Virtual AI Mouse – Gesture Controlled System

This document defines mandatory coding standards and architectural rules for any AI coding assistant (or human contributor) working on this repository. These rules are binding for all code generation, refactoring, and review activity.

---

## 1. Python Version Compatibility

- All code **must** maintain compatibility with **Python 3.11+**.
- Do not use syntax or standard-library features exclusive to versions newer than what is declared in `requirements.txt` / `pyproject.toml` without first updating the declared minimum version.
- Use modern type-hinting syntax (`list[int]`, `str | None`) consistent with 3.11+ conventions.

---

## 2. Project / Folder Structure Rules

- Follow the structure defined in `Architecture.md` §1. Do not introduce new top-level directories without updating `Architecture.md`.
- Source code lives under purpose-named packages: `core/`, `visualization/`, `utils/`, `models/`, `config/`.
- Tests mirror the source structure under `tests/`, with `test_<module_name>.py` naming.
- Hardware mocks live under `tests/mocks/`.

---

## 3. File Naming Conventions

- All Python files: `snake_case.py` (e.g., `gesture_recognizer.py`, not `GestureRecognizer.py`).
- One primary class per file where practical; the file name should reflect the primary class's purpose, not necessarily its exact name.
- Configuration files: `settings.py` (constants only, no logic).

---

## 4. Naming Conventions (PEP 8)

| Element | Convention | Example |
|---------|------------|---------|
| Module/file names | `snake_case` | `hand_detector.py` |
| Class names | `PascalCase` | `GestureRecognizer`, `MouseController` |
| Function/method names | `snake_case` | `compute_finger_states()`, `move_cursor()` |
| Variables | `snake_case` | `frame_width`, `smoothed_x` |
| Constants | `UPPER_SNAKE_CASE` | `CLICK_DISTANCE_THRESHOLD`, `SMOOTHING_FACTOR` |
| Private members | `_leading_underscore` | `_previous_x`, `_debounce_state` |
| Boolean flags | prefixed with `is_`/`has_`/`should_` | `is_drag_active`, `has_hand_detected` |

---

## 5. Constants

- All numeric thresholds (click distance, debounce frame counts, smoothing factors, camera resolution, frame margins) **must** be defined in `config/settings.py` as named `UPPER_SNAKE_CASE` constants.
- **No magic numbers** are permitted directly inside logic modules (`core/`, `utils/`). If a number appears in `gesture_recognizer.py`, `mouse_controller.py`, etc., it must be imported from `settings.py`.
- **Never hardcode screen resolution.** Screen dimensions must always be queried at runtime (e.g., via `pyautogui.size()`) and stored in a `Screen` entity — never assumed as fixed values like `1920x1080`.

---

## 6. Comments and Docstrings

- Every public function/method requires a docstring in **Google-style** format:

```python
def compute_distance(point_a: Landmark, point_b: Landmark) -> float:
    """Computes Euclidean distance between two hand landmarks.

    Args:
        point_a: First landmark with pixel-space x, y coordinates.
        point_b: Second landmark with pixel-space x, y coordinates.

    Returns:
        The Euclidean distance in pixels.
    """
```

- Inline comments should explain **why**, not **what** — avoid comments that simply restate the code.
- Every module file should begin with a short module-level docstring describing its single responsibility.

---

## 7. Type Hints

- **All function signatures must include type hints** for parameters and return values.
- Use `Optional[T]` (or `T | None`) explicitly for nullable returns (e.g., `extract(...) -> Hand | None`).
- Use precise container typing: `list[Landmark]`, `dict[str, GestureAction]`, not bare `list`/`dict`.
- Data model entities (`models/entities.py`) should be implemented as `@dataclass` where practical, for automatic type-safe construction.

---

## 8. Logging Standards

- Use Python's built-in `logging` module exclusively. **Never use bare `print()` for diagnostics or errors** in production code paths (print is acceptable only in throwaway scripts explicitly marked as such).
- Each module obtains its logger via `logging.getLogger(__name__)`.
- Log levels:
  - `DEBUG`: per-frame diagnostic detail (landmark coordinates, raw distances) — disabled by default.
  - `INFO`: lifecycle events (camera opened, application started/stopped).
  - `WARNING`: recoverable issues (optional feature unavailable, fallback config used).
  - `ERROR`: unrecoverable per-operation failures (camera read failure).
  - `CRITICAL`: application cannot continue (camera cannot be opened at all).
- Logging configuration is centralized in `utils/logger.py`; modules must not configure handlers independently.

---

## 9. Error Handling

- Hardware and third-party library calls (`cv2.VideoCapture`, `pyautogui.*`, `pycaw`, `screen_brightness_control`) **must** be wrapped in explicit `try/except` blocks with specific exception types where known.
- Never use bare `except:`; always catch named exceptions (`except OSError as e:`, `except Exception as e:` only as a last-resort boundary with logging).
- Per-frame processing exceptions must be caught **inside the main loop**, logged, and must **not** terminate the application — a single bad frame should never crash a 30-minute session.
- Optional-feature import failures (e.g., `pycaw` not installed or not on Windows) must be caught at import/initialization time and degrade gracefully with a `WARNING` log, not raise at runtime.

---

## 10. Dependency Management

- All dependencies must be declared in `requirements.txt` with **pinned or minimum-bound versions** (e.g., `mediapipe>=0.10`).
- Optional dependencies (`pycaw`, `screen-brightness-control`, `pynput`) should be imported defensively:

```python
try:
    from pycaw.pycaw import AudioUtilities
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False
```

- New dependencies require justification in the pull request description and must not duplicate the functionality of an existing dependency.

---

## 11. Git Commit Conventions

Follow **Conventional Commits**: