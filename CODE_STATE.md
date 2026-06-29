# CODE_STATE.md — Project State and Tracking

## 1. Project Summary
The **Virtual AI Mouse** is a real-time computer vision application that translates hand gestures captured by a standard webcam into system-level mouse, keyboard, and environmental control actions (volume/brightness). It runs entirely locally on Windows (primary target) using Python, OpenCV, MediaPipe, and PyAutoGUI.

### Gesture Features Matrix (Active Tracking)
| Feature / Gesture | Trigger Condition | Action Mapping | Debouncing / Control | Status |
|---|---|---|---|---|
| **Cursor Movement** | Only Index finger extended up | Cursor follows hand tracking landmark | EmaFilter (alpha=0.40) | Active |
| **Left Click / Drag** | Thumb + Index finger tip pinch | `pyautogui.click()` / `pyautogui.mouseDown()` | Debounce persistence frames (3) | Active |
| **Right Click** | Index + Middle pinch, ring+pinky curled | `pyautogui.rightClick()` | Cooldown frames (10) | Active |
| **Double Click** | Thumb + Index + Middle tip pinch | `pyautogui.doubleClick()` | Cooldown frames (10) | Active |
| **Scroll Mode** | Only Middle finger extended up | `pyautogui.scroll()` | Vertical delta movement | Active |
| **Presentation Slide Next** | Only Thumb extended up | `pyautogui.press('right')` | Cooldown frames (15) | Active |
| **Presentation Slide Prev** | Only Thumb extended down | `pyautogui.press('left')` | Cooldown frames (15) | Active |
| **Volume Control** | Index, Middle, Ring up, Pinky curled | `pyautogui.press('volumeup')` (up) / `pyautogui.press('volumedown')` (down) | Cooldown frames (5), vertical delta movement | Active |
| **Page Up / Down** | Index, Middle, Ring, Pinky up, Thumb tucked | `pyautogui.press('pageup')` (up) / `pyautogui.press('pagedown')` (down) | Cooldown frames (15), anchor delta | Active |
| **Zoom In / Out** | Thumb + Index extended, others curled (non-L-shape) | Hold `ctrl` and `pyautogui.scroll(100)` (in) / `pyautogui.scroll(-100)` (out) | Zoom distance dead-zone buffer (1.25x / 0.75x of baseline) | Active |
| **Brightness Control** | Thumb + Index extended (L-shape / pistol at ~90 deg), others curled | SBC change brightness / PowerShell WMI Fallback | Vertical delta movement of tracking landmark | Active |

## 2. Constraints and Rules
- **Python Compatibility**: Python 3.11+ (using modern type hints, e.g., `list[int]`, `str | None`).
- **Performance Budget**: Sustained frame rate of $\ge 15\text{ FPS}$ (target 20-30 FPS) with a per-frame processing budget of $\le 66\text{ms}$.
- **Memory Footprint**: Stable memory usage over time with no unbounded growth.
- **Coordinate Mapping**: 
  - Never hardcode screen resolution. Retrieve it dynamically at runtime using `pyautogui.size()`.
  - Use a "Tracking Window/Zone" (e.g., inset margins of 20% to 80% of webcam frame size) mapped to the full screen to allow easier reachability of screen corners.
- **No Magic Numbers**: All configuration parameters, gesture thresholds, click distances, and smoothing factors must reside in `config/settings.py`.
- **Centralized Logging**: Direct all logs through `logging.getLogger(__name__)` configured in `utils/logger.py`. Do not use raw `print()` calls in production code paths.
- **Graceful Error Recovery**: Catch per-frame perception or OS execution failures inside the main loop to keep the application running. Gracefully degrade if optional libraries (like `pycaw`) fail to import.

## 3. Planned File Tree
```text
Virtual-AI-Mouse/
├── CODE_STATE.md                    # Project state tracking
├── main.py                          # Application entry point; orchestrates the main loop
├── requirements.txt                 # Python dependencies
├── config/
│   ├── __init__.py
│   └── settings.py                  # Constants and configuration
├── models/
│   ├── __init__.py
│   └── entities.py                  # Data classes: Hand, Landmark, Gesture, Cursor
├── core/
│   ├── __init__.py
│   ├── camera_module.py             # OpenCV camera loop and resolution config
│   ├── hand_detector.py             # MediaPipe Hands wrapper
│   ├── landmark_extractor.py        # Converts MediaPipe landmarks to pixel coordinates
│   ├── gesture_recognizer.py        # Gesture rules/mapping logic
│   ├── mouse_controller.py          # Coordinates, mapping, PyAutoGUI actions
│   ├── presentation_controller.py   # Key sends for presentation slides
│   └── system_controller.py         # Pycaw / screen-brightness-control integrations
├── visualization/
│   ├── __init__.py
│   └── overlay_renderer.py          # Draws landmarks, bounding box, text, metrics
├── utils/
│   ├── __init__.py
│   ├── geometry.py                  # Distance, math helpers
│   ├── smoothing.py                 # Smoothing algorithms (EMA)
│   ├── debounce.py                  # Debounce & state persistence trackers
│   └── logger.py                    # Shared logging config
└── tests/
    ├── __init__.py
    ├── test_geometry.py
    ├── test_smoothing.py
    ├── test_gesture_recognizer.py
    └── mocks/
        ├── __init__.py
        └── mock_camera.py           # Virtual camera mock for headless testing
```

## 4. Completed Steps
- [x] Inspected workspace and read system documentation (`AGENTS.md`, `ARCHITECTURE.md`, `PRD.md`, `SRS.md`).
- [x] Formulated file structure and identified required packages.
- [x] Created/initialized `CODE_STATE.md`.
- [x] Created `requirements.txt` file listing core and optional dependencies.
- [x] Implemented data models (`models/entities.py`).
- [x] Implemented configuration system (`config/settings.py`).
- [x] Implemented utility modules (`utils/logger.py`, `utils/geometry.py`, `utils/smoothing.py`, `utils/debounce.py`).
- [x] Implemented core perception modules (`core/camera_module.py`, `core/hand_detector.py`, `core/landmark_extractor.py`).
- [x] Implemented gesture recognition module (`core/gesture_recognizer.py`).
- [x] Implemented action execution controllers (`core/mouse_controller.py`, `core/presentation_controller.py`, `core/system_controller.py`).
- [x] Implemented HUD and visual overlay (`visualization/overlay_renderer.py`).
- [x] Implemented core loop orchestrator (`main.py`).
- [x] Implemented geometry, smoothing, and gesture unit tests (`tests/test_geometry.py`, `tests/test_smoothing.py`, `tests/test_gesture_recognizer.py`).
- [x] Implemented headless test runner (`tests/run_tests.py`) and loop profiler (`utils/profiler.py`).
- [x] Migrated perception pipeline to modern MediaPipe Tasks Vision API and implemented matching unit tests (`tests/test_hand_detector.py`, `tests/test_landmark_extractor.py`).
- [x] Verified and validated code correctness (20/20 test assertions passing).
- [x] Applied latency optimization updates: clamped camera capture resolution to 640x480, verified MediaPipe HandLandmarker RunningMode.VIDEO tracking, and increased the cursor smoothing alpha factor to 0.40.

## 5. Pending Steps
- None. (All phases completed successfully).

## 6. Decisions Made
- **Smoothing Algorithm**: One-Euro Filter or Exponential Moving Average (EMA). We will start with EMA (configurable smoothing factor $\alpha$) as it is simpler, and fallback/upgrade to One-Euro Filter if high-speed responsiveness requires dynamic jitter correction.
- **MediaPipe Tasks API Migration**: Migrated the hand perception pipeline from legacy `mediapipe.solutions.hands` (unsupported/removed in modern environments like Python 3.13) to the modern MediaPipe Tasks Vision API (`mediapipe.tasks.python.vision`).
  - Implemented automatic runtime check and download of the `hand_landmarker.task` file at the root workspace directory if it is missing at startup.
  - Added `MP_MODEL_ASSET_PATH` to configuration settings.
  - Implemented a backward-compatible monkey-patch for `mp.Image.create_from_numpy_image` to ensure reliability across all MediaPipe 0.10+ environments.
  - Updated the landmark extractor logic to natively parse the `HandLandmarkerResult` format and sanitize handedness strings (e.g., "Right", "Left").
- **Pipeline Latency & Performance Optimizations**:
  - Configured `pyautogui.PAUSE = 0.0` inside `main.py` and `core/mouse_controller.py` to completely eliminate PyAutoGUI's default 0.1-second artificial delay on every action trigger.
  - Configured the Hand Landmarker setup to run in `RunningMode.VIDEO` during active webcam streams to leverage temporal frame-to-frame tracking and internal caching, substantially reducing per-frame inference time.
  - Enforced `max_num_hands = 1` to prevent redundant computing on extra hands.
  - Clamped camera capture resolution properties in `core/camera_module.py` to exactly 640x480 to reduce image ingestion and downscaling overhead.
  - Adjusted the Exponential Moving Average cursor smoothing alpha factor to 0.40 in `config/settings.py` to minimize the historical lag window.
- **Gesture Detection Strategy**: Hybrid system using finger states (up/down vector `[thumb, index, middle, ring, pinky]`) combined with pairwise Euclidean distances for fine control (pinches).
- **Click Thresholds**: Normalised distance between thumb tip and index tip (or other finger tips). Standard threshold is set to $\le 0.05$ of the hand bounding box diagonal to account for distance from camera.
- **Debouncing**: Gestures must persist for at least 3 consecutive frames to trigger an action (state transition), minimizing spurious detections.
- **Testing Framework**: `pytest` was selected to write and execute unit and integration tests.
- **Cross-Platform System Controls**: Non-Windows platforms (macOS/Linux) will utilize logged placeholder implementations for volume and brightness control to avoid startup/runtime exceptions.

## 7. Validation Status
- Current Status: **Stable**
  - Unit Tests: 20/20 passing on geometry, smoothing, gesture recognition, hand detection, and landmark extraction.
  - Coordinate Clamping: 100% boundary safety.
  - Smoothing Filter: Tremor smoothing active.
  - Performance: Frame processing loop uses the `PipelineProfiler` to verify the $\le 66\text{ms}$ budget is not breached.
  - Configuration Alignment: Added the missing `IS_DEBUG_MODE` flag to `config/settings.py` to prevent AttributeErrors on startup.
  - Perception & Action Layers: Fully stable, leveraging temporal frame-to-frame video mode tracking and zero-latency mouse controllers (`pyautogui.PAUSE = 0.0`).

## 8. Next Steps
1. Execute `python main.py` to start the live application.
2. Conduct manual gesture usability checks.














