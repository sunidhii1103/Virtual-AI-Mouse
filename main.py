"""Main orchestrator for the Virtual AI Mouse application.

This module initializes the camera, hand detection pipeline, gesture recognition,
and OS interaction controllers, and runs the high-performance execution loop.
"""

import time
import logging
import cv2
import pyautogui
from utils.logger import setup_logging
from utils.profiler import PipelineProfiler
import config.settings as cfg
from core.camera_module import CameraModule, CameraError
from core.hand_detector import HandDetector
from core.landmark_extractor import LandmarkExtractor
from core.gesture_recognizer import GestureRecognizer
from core.mouse_controller import MouseController
from core.presentation_controller import PresentationController
from core.system_controller import SystemController
from visualization.overlay_renderer import OverlayRenderer
from utils.geometry import compute_hand_scale, compute_normalized_distance

# Set up logging early
setup_logging(debug_mode=cfg.IS_DEBUG_MODE)
logger = logging.getLogger("main")


def main() -> None:
    """Entry point to initialize subsystems and execute the perception-action cycle."""
    logger.info("Starting Virtual AI Mouse application...")

    # Configure PyAutoGUI fail-safe
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.0

    # Instantiate modules
    detector = HandDetector()
    extractor = LandmarkExtractor()
    recognizer = GestureRecognizer()
    mouse_ctrl = MouseController()
    pres_ctrl = PresentationController()
    sys_ctrl = SystemController()
    renderer = OverlayRenderer()
    profiler = PipelineProfiler(warning_threshold_ms=66.0)

    # Determine system status warning
    system_status = "System OK"
    if sys_ctrl._volume_interface is None:
        system_status = "OS Controls Disabled"

    # Tracking states
    prev_tracking_y: float | None = None
    prev_zoom_dist: float | None = None
    prev_page_nav_y: float | None = None
    page_nav_cooldown_counter: int = 0
    fps = cfg.CAMERA_FPS
    last_frame_time = time.perf_counter()

    logger.info("Webcam starting. Press ESC or 'q' in the camera window to exit.")

    try:
        with CameraModule() as camera:
            while True:
                frame_start = time.perf_counter()
                profiler.clear()

                # 1. Ingest frame
                with profiler.profile("Frame Ingestion Time"):
                    frame = camera.read_frame()

                if frame is None:
                    # Non-blocking skip on empty frames
                    time.sleep(0.01)
                    continue

                frame_height, frame_width = frame.shape[:2]

                # 2. Hand detection (Perception Phase 1)
                with profiler.profile("Perception Framework Overhead"):
                    detection_results = detector.detect_hands(frame)

                # 3. Landmark extraction (Perception Phase 2)
                with profiler.profile("Landmark Extraction"):
                    hand = extractor.extract(detection_results, frame_width, frame_height)

                active_gesture_label = cfg.GESTURE_NONE
                is_inside_zone = True

                if hand:
                    # Extract tracking landmark (Index fingertip, index 8)
                    tracking_lm = hand.landmarks[8]

                    # Verify if tracking point is within the interaction zone
                    xmin = frame_width * cfg.TRACKING_ZONE_X_MIN
                    xmax = frame_width * cfg.TRACKING_ZONE_X_MAX
                    ymin = frame_height * cfg.TRACKING_ZONE_Y_MIN
                    ymax = frame_height * cfg.TRACKING_ZONE_Y_MAX

                    is_inside_zone = (
                        xmin <= tracking_lm.x <= xmax and ymin <= tracking_lm.y <= ymax
                    )

                    # Draw hand skeleton overlay
                    renderer.draw_hand_skeleton(frame, hand)

                    # 4. Gesture recognition (Interpretation Phase)
                    with profiler.profile("Gesture Reasoning Latency"):
                        gesture = recognizer.recognize_gesture(hand)
                    active_gesture_label = gesture.label

                    # Reset non-active gesture tracking states
                    if gesture.label != cfg.GESTURE_ZOOM_PINCH:
                        prev_zoom_dist = None
                    if gesture.label != cfg.GESTURE_PAGE_NAV:
                        prev_page_nav_y = None

                    # 5. Command dispatch (Action Phase)
                    with profiler.profile("Action Controller Execution Time"):
                        if is_inside_zone:
                            # Move cursor on MOVE, CLICK_LEFT, and ZOOM gestures
                            if gesture.label in [
                                cfg.GESTURE_MOVE,
                                cfg.GESTURE_CLICK_LEFT,
                                cfg.GESTURE_ZOOM,
                            ]:
                                mouse_ctrl.map_and_move_cursor(
                                    tracking_lm, frame_width, frame_height
                                )

                            # Trigger Clicks
                            if gesture.label == cfg.GESTURE_CLICK_LEFT:
                                mouse_ctrl.execute_left_click()
                                mouse_ctrl.handle_drag_state(should_drag=True)
                            else:
                                # Release drag if not in click/drag gesture
                                mouse_ctrl.handle_drag_state(should_drag=False)

                            if gesture.label == cfg.GESTURE_CLICK_RIGHT:
                                mouse_ctrl.execute_right_click()

                            if gesture.label == cfg.GESTURE_CLICK_DOUBLE:
                                mouse_ctrl.execute_double_click()

                            # Slide Navigation (Presentation)
                            if gesture.label in [cfg.GESTURE_SLIDE_NEXT, cfg.GESTURE_SLIDE_PREV]:
                                pres_ctrl.handle_gesture(gesture.label)

                            # Zoom In / Zoom Out (Pinch Gun gesture)
                            if gesture.label == cfg.GESTURE_ZOOM_PINCH:
                                scale = compute_hand_scale(hand.landmarks)
                                curr_zoom_dist = compute_normalized_distance(
                                    hand.landmarks[4], hand.landmarks[8], scale
                                )
                                if prev_zoom_dist is not None:
                                    if curr_zoom_dist > prev_zoom_dist * cfg.ZOOM_IN_MULTIPLIER:
                                        pyautogui.keyDown("ctrl")
                                        pyautogui.scroll(100)
                                        pyautogui.keyUp("ctrl")
                                        logger.info("Zoom Action: Zoom In (ctrl + scroll up)")
                                        prev_zoom_dist = curr_zoom_dist
                                    elif curr_zoom_dist < prev_zoom_dist * cfg.ZOOM_OUT_MULTIPLIER:
                                        pyautogui.keyDown("ctrl")
                                        pyautogui.scroll(-100)
                                        pyautogui.keyUp("ctrl")
                                        logger.info("Zoom Action: Zoom Out (ctrl + scroll down)")
                                        prev_zoom_dist = curr_zoom_dist
                                else:
                                    prev_zoom_dist = curr_zoom_dist

                            # Vertical delta calculation for scrolling, volume, brightness, and page nav
                            if prev_tracking_y is not None:
                                delta_y = tracking_lm.y - prev_tracking_y
                                # Threshold in pixels to prevent minor jitter from scrolling/adjusting
                                move_threshold = cfg.MOVE_THRESHOLD

                                if abs(delta_y) > move_threshold:
                                    increase_value = delta_y < 0  # y decreases moving up

                                    if gesture.label == cfg.GESTURE_SCROLL:
                                        # Scroll amount (positive up, negative down)
                                        scroll_amt = 120 if increase_value else -120
                                        pyautogui.scroll(scroll_amt)

                                    elif gesture.label == cfg.GESTURE_ZOOM:
                                        # Zoom: ctrl + scroll
                                        scroll_amt = 100 if increase_value else -100
                                        pyautogui.keyDown("ctrl")
                                        pyautogui.scroll(scroll_amt)
                                        pyautogui.keyUp("ctrl")

                                    elif gesture.label == cfg.GESTURE_VOLUME:
                                        sys_ctrl.change_volume(increase=increase_value)

                                    elif gesture.label == cfg.GESTURE_BRIGHTNESS:
                                        sys_ctrl.change_brightness(increase=increase_value)

                                # Page Up / Page Down (Web Browsing Navigation)
                                if gesture.label == cfg.GESTURE_PAGE_NAV:
                                    if page_nav_cooldown_counter == 0:
                                        if prev_page_nav_y is None:
                                            prev_page_nav_y = tracking_lm.y

                                        delta_page_y = tracking_lm.y - prev_page_nav_y
                                        page_threshold = cfg.PAGE_NAV_THRESHOLD

                                        if delta_page_y < -page_threshold:
                                            pyautogui.press("pageup")
                                            page_nav_cooldown_counter = cfg.PAGE_NAV_COOLDOWN_FRAMES
                                            logger.info("Page Action: Page Up")
                                            prev_page_nav_y = tracking_lm.y
                                        elif delta_page_y > page_threshold:
                                            pyautogui.press("pagedown")
                                            page_nav_cooldown_counter = cfg.PAGE_NAV_COOLDOWN_FRAMES
                                            logger.info("Page Action: Page Down")
                                            prev_page_nav_y = tracking_lm.y
                                    else:
                                        # Keep updating anchor while on cooldown to prevent jump triggers right after cooldown
                                        prev_page_nav_y = tracking_lm.y

                            # Save previous tracking y
                            prev_tracking_y = tracking_lm.y

                        else:
                            # Hand is out of bounds; release drag and reset cursor filters
                            mouse_ctrl.reset_filters()
                            prev_tracking_y = None
                            prev_zoom_dist = None
                            prev_page_nav_y = None
                else:
                    # No hand detected; reset cursor filters and tracking history
                    mouse_ctrl.reset_filters()
                    prev_tracking_y = None
                    prev_zoom_dist = None
                    prev_page_nav_y = None

                # Update click, presentation, and page nav cooldown counters
                mouse_ctrl.update_cooldown()
                pres_ctrl.update_cooldown()
                if page_nav_cooldown_counter > 0:
                    page_nav_cooldown_counter -= 1

                # Verify latency budget and log warnings if needed
                profiler.log_and_verify_budget()

                # Calculate Loop Latency and FPS
                frame_end = time.perf_counter()

                # Compute running FPS
                delta_time = frame_end - last_frame_time
                if delta_time > 0:
                    current_fps = 1.0 / delta_time
                    fps = 0.9 * fps + 0.1 * current_fps
                last_frame_time = frame_end

                # 6. Render UI details (Presentation Phase)
                renderer.draw_tracking_zone(frame, is_inside=is_inside_zone)
                renderer.draw_hud(frame, fps, active_gesture_label, system_status)

                # Show frame
                cv2.imshow(cfg.WINDOW_NAME, frame)

                # Keyboard interrupts monitoring
                key = cv2.waitKey(1) & 0xFF
                if key == 27 or key == ord("q"):  # ESC or 'q'
                    logger.info("User interrupt signal received. Exiting...")
                    break

    except CameraError as e:
        logger.critical("Unrecoverable camera error: %s", e)
    except Exception as e:
        logger.critical("Unexpected application crash: %s", e)
    finally:
        # Clean shutdown and resource release
        logger.info("Cleaning up OpenCV resources and closing window handles...")
        detector.close()
        cv2.destroyAllWindows()
        logger.info("Virtual AI Mouse application shut down successfully.")


if __name__ == "__main__":
    main()
