# PRD.md — Product Requirements Document

## Virtual AI Mouse – Gesture Controlled System

---

## 1. Product Overview

The **Virtual AI Mouse** is a desktop computer vision application that replaces the conventional physical mouse with real-time hand gesture recognition. Using a standard webcam, the system captures live video, detects and tracks 21 hand landmarks via Google's MediaPipe framework, interprets finger configurations into discrete gestures, and translates those gestures into mouse and system-level actions (cursor movement, clicks, scrolling, drag-and-drop, zoom, and presentation control) using PyAutoGUI.

The product is designed as a **touchless human-computer interaction (HCI) layer** that runs entirely on the local machine, with no cloud dependency, no authentication, and no persistent user data storage in its initial release.

---

## 2. Organization

**Organization Name:** NeuraLoop Systems
**Division:** NeuraLoop Labs – Human-Computer Interaction Research Unit
**Mission:** To build natural, low-friction interfaces that reduce the dependency on traditional input hardware through applied computer vision and machine perception.

NeuraLoop Systems is a fictional applied-AI software studio specializing in real-time perception systems for accessibility, productivity, and human-computer interaction use cases.

---

## 3. Vision Statement

> "To make touchless, gesture-driven interaction with computers as natural and reliable as using a physical mouse — accessible to anyone, on any standard webcam, without specialized hardware."

---

## 4. Business Problem

Traditional input devices (mice, trackpads) require:

- Physical contact, which is a barrier for users with motor impairments or limited dexterity.
- A flat surface and unobstructed hand movement, which is inconvenient in presentation, kiosk, or hygiene-sensitive environments.
- Additional hardware procurement and maintenance.

There is a growing need for **contactless, camera-based interaction systems** that work using commodity hardware (a standard webcam) rather than specialized sensors (e.g., depth cameras, LeapMotion, or wearables). Existing gesture-control solutions are often proprietary, hardware-locked, or limited to narrow use cases (e.g., only presentation control). There is a gap for an **open, extensible, software-only gesture mouse** that covers the full range of standard mouse operations.

---

## 5. Project Objectives

1. Provide real-time, low-latency hand tracking using a standard webcam.
2. Translate recognized hand gestures into standard mouse operations (move, click, scroll, drag).
3. Provide additional touchless system controls (volume, brightness, slide navigation, zoom).
4. Ensure the system is usable across varied lighting and background conditions.
5. Maintain a modular, extensible architecture that allows new gestures and modules to be added without rewriting the core pipeline.
6. Deliver a smooth user experience through coordinate interpolation and cursor smoothing, minimizing jitter.
7. Keep the system fully local — no network calls, no telemetry, no external data persistence.

---

## 6. Scope

### In Scope
- Real-time webcam-based hand detection and 21-point landmark tracking (single hand, primary release).
- Cursor movement, left click, right click, double click, drag-and-drop, scroll, zoom gestures.
- Presentation slide navigation (next/previous).
- Optional volume and brightness control via gesture distance mapping.
- On-screen visualization: landmark overlay, bounding box, FPS counter, active gesture label.
- Configurable gesture-to-action mapping via constants/configuration file.
- Windows OS as the primary supported platform.

### Out of Scope (Current Release)
- Multi-hand simultaneous control.
- Cloud sync, user accounts, authentication.
- Mobile platform support.
- Voice command integration.
- AI-based adaptive/learned gesture customization.
- Cross-platform guaranteed parity (macOS/Linux are best-effort, not guaranteed).

---

## 7. User Personas

### Persona 1 — "Aditi the Presenter"
- **Role:** University lecturer / corporate trainer.
- **Goal:** Navigate slides and control the cursor while standing away from the laptop.
- **Pain point:** Constantly returning to the laptop to click "next slide" breaks presentation flow.

### Persona 2 — "Rohan the Developer"
- **Role:** Software engineer, early technology adopter.
- **Goal:** Experiment with gesture-based control as an alternative input method and extend the project with custom gestures.
- **Pain point:** Wants an open, hackable codebase rather than a closed proprietary tool.

### Persona 3 — "Meera the Accessibility User"
- **Role:** User with limited fine motor control in fingers/wrist, making physical mouse use difficult.
- **Goal:** Operate the desktop using broader hand/arm movements instead of precise mouse clicks.
- **Pain point:** Most accessibility tools are hardware-dependent and expensive.

### Persona 4 — "Sahil the Student"
- **Role:** Computer science student.
- **Goal:** Learn computer vision and HCI concepts through a hands-on, well-documented open project.
- **Pain point:** Most tutorials online are fragmented and lack production-quality structure.

---

## 8. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR-1 | The system shall capture continuous video frames from a connected webcam. |
| FR-2 | The system shall detect the presence of a hand within each frame using MediaPipe Hands. |
| FR-3 | The system shall extract 21 hand landmarks with pixel-space (x, y) coordinates per detected hand. |
| FR-4 | The system shall determine the up/down state of each of the five fingers per frame. |
| FR-5 | The system shall map a recognized finger-state pattern to a discrete gesture label. |
| FR-6 | The system shall move the system cursor when the "cursor move" gesture is active, using interpolated and smoothed coordinates. |
| FR-7 | The system shall trigger a left click when the index-thumb pinch gesture is detected below a configurable distance threshold. |
| FR-8 | The system shall trigger a right click when the index-middle pinch gesture is detected. |
| FR-9 | The system shall trigger a double click when the thumb-index-middle gesture is detected. |
| FR-10 | The system shall support drag-and-drop by sustaining a "click-hold" state across frames until release gesture is detected. |
| FR-11 | The system shall scroll up/down based on vertical hand movement while in "scroll" gesture state. |
| FR-12 | The system shall trigger zoom in/out based on increasing/decreasing distance between two fingers. |
| FR-13 | The system shall trigger next/previous slide actions based on thumb-up/thumb-down gestures. |
| FR-14 | The system shall optionally map hand-distance to system volume level. |
| FR-15 | The system shall optionally map hand-distance to system brightness level. |
| FR-16 | The system shall render a live visualization overlay including landmarks, bounding box, FPS, and current gesture label. |
| FR-17 | The system shall allow the user to exit the application via a defined keyboard interrupt (e.g., `ESC`). |
| FR-18 | The system shall load all gesture-action mappings and thresholds from a centralized configuration module. |

---

## 9. Non-Functional Requirements

| ID | Category | Requirement |
|----|----------|-------------|
| NFR-1 | Performance | The system shall maintain a minimum of 15–20 FPS on standard consumer hardware (Intel i5 or equivalent, no dedicated GPU required). |
| NFR-2 | Latency | End-to-end gesture-to-action latency shall not exceed 100ms under normal operating conditions. |
| NFR-3 | Usability | Cursor movement shall be smoothed to avoid visible jitter; raw landmark jitter shall not propagate directly to cursor position. |
| NFR-4 | Reliability | The system shall recover gracefully from temporary loss of hand detection (e.g., hand leaves frame) without crashing. |
| NFR-5 | Portability | The core detection and gesture logic shall be OS-agnostic; only system-action execution (PyAutoGUI, volume/brightness libraries) may be OS-specific. |
| NFR-6 | Maintainability | The codebase shall be modular, with each major capability isolated into an independently testable module. |
| NFR-7 | Configurability | Thresholds (click distance, smoothing factor, frame reduction margins) shall be externally configurable without code changes. |
| NFR-8 | Privacy | No video frame or landmark data shall be persisted to disk or transmitted over a network by default. |
| NFR-9 | Accessibility | The gesture set shall avoid requiring fine, high-precision finger movements wherever a coarser alternative is feasible. |

---

## 10. User Stories

1. **As a presenter**, I want to move to the next slide by raising my thumb, so that I can control my presentation without touching my laptop.
2. **As a developer**, I want a clear FPS overlay, so that I can verify the gesture pipeline is performing well during testing.
3. **As an accessibility user**, I want to click by simply pinching my fingers together, so that I don't need fine motor control to operate a physical mouse button.
4. **As a student**, I want each module (camera, detection, gesture recognition, mouse control) to be separated, so that I can learn and modify one part without breaking the others.
5. **As a user**, I want the cursor to move smoothly rather than jump erratically, so that the experience feels natural.
6. **As a user**, I want to scroll a webpage using a single-finger gesture, so that I can browse without a physical mouse.
7. **As a user**, I want to drag and drop a file/window, so that I can perform basic desktop file operations gesture-only.
8. **As a power user**, I want to adjust system volume and brightness with hand distance, so that I have full touchless control of my environment.
9. **As a user**, I want to exit the application safely with a single keypress, so that I always have a reliable way to stop the program.

---

## 11. Core Features

| Feature | Description |
|---------|-------------|
| Real-Time Hand Tracking | Detects hand and extracts 21 landmarks per frame via MediaPipe. |
| Cursor Control | Maps index-finger position to screen coordinates with interpolation and smoothing. |
| Click Gestures | Left click, right click, double click via finger-pinch distance thresholds. |
| Drag and Drop | Sustained pinch gesture mapped to mouse-down/mouse-up sequence. |
| Scroll Control | Vertical hand movement mapped to scroll-up/scroll-down events. |
| Zoom Control | Two-finger distance change mapped to zoom-in/zoom-out key combinations. |
| Presentation Control | Thumb-up/thumb-down mapped to next/previous slide key events. |
| Volume Control (optional) | Hand-distance mapped to system volume via Pycaw. |
| Brightness Control (optional) | Hand-distance mapped to screen brightness via screen-brightness-control. |
| Visualization Overlay | Real-time rendering of landmarks, bounding box, FPS, and active gesture. |
| Gesture Configuration | Centralized, constants-driven gesture-to-action mapping. |

---

## 12. User Flows

### Flow 1 — Launch Application
1. User runs `main.py`.
2. Application initializes configuration, logging, and camera module.
3. Main loop starts.

### Flow 2 — Webcam Initialization
1. System requests video capture device (default index 0).
2. On success: proceed to frame capture loop.
3. On failure: log error, display message, exit gracefully.

### Flow 3 — Hand Detection
1. Frame is read from camera.
2. Frame is converted (BGR→RGB) and passed to MediaPipe Hands.
3. If hand(s) detected: landmarks extracted; else: frame passed through with "no hand" state.

### Flow 4 — Cursor Movement
1. Index fingertip landmark (id 8) coordinates extracted.
2. Coordinates interpolated from webcam resolution to screen resolution.
3. Smoothing algorithm applied to interpolated coordinates.
4. PyAutoGUI moves cursor to smoothed coordinates.

### Flow 5 — Gesture Recognition
1. Finger-state vector computed (`[thumb, index, middle, ring, pinky]` as 1/0).
2. Finger-state vector and relevant landmark distances matched against configured gesture definitions.
3. Matching gesture label returned to the controller layer.

### Flow 6 — Mouse Click
1. Gesture recognized as "left click" / "right click" / "double click."
2. Distance threshold validated to avoid false triggers.
3. PyAutoGUI executes corresponding click action.
4. Cooldown/debounce timer started to prevent repeated triggering in consecutive frames.

### Flow 7 — Scroll
1. Gesture recognized as "scroll mode."
2. Vertical delta of hand position across frames computed.
3. Scroll direction and magnitude mapped to `pyautogui.scroll()` calls.

### Flow 8 — Presentation Mode
1. Gesture recognized as thumb-up or thumb-down.
2. Corresponding keyboard event (e.g., Right Arrow / Left Arrow, or PageDown/PageUp) is dispatched.
3. Debounce applied to prevent multiple slide jumps per gesture hold.

### Flow 9 — Exit Application
1. User presses configured exit key (default: `ESC`) in the OpenCV window.
2. Main loop breaks.
3. Camera resource released, OpenCV windows destroyed, application terminates cleanly.

---

## 13. Success Metrics

| Metric | Target |
|--------|--------|
| Average FPS during operation | ≥ 15–20 FPS on standard hardware |
| Gesture recognition accuracy | ≥ 90% under controlled lighting |
| False click trigger rate | < 5% of intentional gesture attempts |
| Cursor jitter (visual stability) | No perceptible jump > smoothing-defined threshold |
| Application crash rate | Zero crashes during a 30-minute continuous session |
| Setup time for new user | < 10 minutes from clone to running application |

---

## 14. Assumptions

- The user has a functioning, reasonably well-lit webcam (built-in or USB).
- The host machine meets minimum CPU requirements for real-time MediaPipe inference.
- The user operates in an environment with a mostly unobstructed view of one hand.
- Windows is the primary OS target; macOS/Linux compatibility is best-effort due to PyAutoGUI/Pycaw/brightness-control library variances.
- The user has administrative permission to install Python packages in their environment.

---

## 15. Risks

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Poor lighting reduces detection accuracy | High | Medium | Provide lighting guidance; consider adaptive preprocessing in future versions. |
| False gesture triggers cause unintended clicks | Medium | Medium | Use debounce timers and distance thresholds; require gesture persistence over multiple frames. |
| Cross-platform inconsistency (Pycaw is Windows-only) | Medium | High | Clearly document optional features as Windows-only; provide graceful fallback. |
| High CPU usage on low-end hardware | Medium | Medium | Allow frame resolution/processing rate to be configurable. |
| Webcam access denied by OS privacy settings | Low | Low | Provide clear error messaging and setup documentation. |
| Background clutter/multiple hands causing misdetection | Medium | Medium | Restrict to single dominant hand in v1; document testing recommendations. |

---

## 16. Future Roadmap

| Phase | Enhancement |
|-------|-------------|
| Phase 2 | Multi-hand support (two-hand gestures, two-cursor scenarios). |
| Phase 2 | User-configurable gesture customization via settings UI. |
| Phase 3 | AI-based adaptive gesture learning (per-user calibration model). |
| Phase 3 | Voice assistant integration for hybrid voice+gesture control. |
| Phase 4 | Cross-platform parity (macOS/Linux native support for all optional modules). |
| Phase 4 | Custom gesture recording and training pipeline. |
| Phase 5 | User settings/profile management with persistent local configuration profiles. |

---