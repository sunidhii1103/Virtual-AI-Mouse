| Trigger Condition | Resulting Event |
|--------------------|------------------|
| Only index finger up, persisted ≥ N frames | `MOUSE_MOVE` event stream begins |
| Thumb-index distance < threshold | `MOUSE_CLICK` (left) event, debounced |
| Index-middle distance < threshold | `MOUSE_CLICK` (right) event, debounced |
| Thumb-index-middle convergence | `MOUSE_CLICK` (double) event, debounced |
| Sustained pinch + movement | `MOUSE_DRAG` start; release on pinch release |
| Middle-finger-only + vertical delta | `SCROLL` event, magnitude proportional to delta |
| Two-finger distance delta beyond threshold | `ZOOM` event (in/out based on sign of delta) |
| Thumb-up / thumb-down, debounced | `SLIDE_NAV` (next/previous) event |
| Hand-distance range mapped (optional mode active) | `VOLUME` or `BRIGHTNESS` event |
| Exit key pressed | `APPLICATION_EXIT` event |

---

## 16. Error Handling Requirements

| Condition | Required Behavior |
|-----------|---------------------|
| Camera fails to open | Log error via `logging.error`; display user-facing message; exit with non-zero status. |
| Camera disconnects mid-session | Catch read failure; attempt limited reconnection retries; if unsuccessful, terminate gracefully with logged error. |
| No hand detected in frame | Suppress gesture-dependent logic for that frame; continue loop without exception. |
| MediaPipe inference exception | Catch and log; skip frame; continue loop (must not crash the application). |
| PyAutoGUI action failure (e.g., permissions) | Catch exception; log warning; continue operation without terminating the session. |
| Pycaw/brightness-control unavailable (non-Windows or missing dependency) | Detect at startup; disable optional feature with a logged warning rather than failing application startup. |
| Invalid/missing configuration value | Fall back to documented default; log warning indicating fallback was used. |

---

## 17. Performance Expectations

| Metric | Expectation |
|--------|--------------|
| Sustained frame rate | ≥ 15 FPS minimum, 20–30 FPS target on recommended hardware |
| Per-frame processing budget | ≤ 66ms (to sustain ≥ 15 FPS) |
| Memory usage | Stable over time; no unbounded growth across a continuous session |
| Startup time | ≤ 5 seconds from launch to first rendered frame |
| Resource cleanup | Camera handle and OpenCV windows released within 1 second of exit trigger |

---