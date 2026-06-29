"""Model setup utility for downloading MediaPipe hand landmarker bundle.

This script fetches the official Google MediaPipe hand landmarker task model
and stores it in the models/ directory for local offline use.
"""

import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("setup_model")

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "hand_landmarker.task")


def download_model() -> None:
    """Downloads the hand landmarker model to the models/ directory."""
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
        logger.info("Created directory: %s", MODEL_DIR)

    if os.path.exists(MODEL_PATH):
        logger.info("Model file already exists at: %s", MODEL_PATH)
        return

    logger.info("Downloading MediaPipe Hand Landmarker model from: %s", MODEL_URL)
    try:
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        logger.info("Download completed successfully! Saved to: %s", MODEL_PATH)
    except Exception as e:
        logger.error("Failed to download model: %s", e)
        raise e


if __name__ == "__main__":
    download_model()
