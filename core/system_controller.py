"""System controller module for the Virtual AI Mouse system.

This module maps gestures to OS-level system parameter modifications, including
audio volume and screen brightness, with defensive cross-platform fallbacks.
"""

import sys
import logging
import subprocess

logger = logging.getLogger(__name__)

# Defensive imports for volume control (Windows-specific COM API)
PYCAW_AVAILABLE = False
if sys.platform == "win32":
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        PYCAW_AVAILABLE = True
    except ImportError:
        logger.warning(
            "pycaw or comtypes is not installed. Volume control fallback will be used."
        )
    except Exception as e:
        logger.warning(
            "Failed to initialize COM dependencies for pycaw: %s. Volume control will fall back.",
            e,
        )

# Defensive imports for screen brightness control
SBC_AVAILABLE = False
try:
    import screen_brightness_control as sbc
    SBC_AVAILABLE = True
except ImportError:
    logger.warning(
        "screen-brightness-control is not installed. Brightness control fallback will be used."
    )
except Exception as e:
    logger.warning("Failed to initialize screen-brightness-control: %s", e)


class SystemController:
    """Manages system-level audio volume and monitor brightness adjustments."""

    def __init__(self) -> None:
        """Initializes the SystemController with native OS interfaces."""
        self._volume_interface = None
        self._is_windows = sys.platform == "win32"

        if self._is_windows and PYCAW_AVAILABLE:
            try:
                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))
                logger.info("Volume Control interface successfully initialized.")
            except Exception as e:
                logger.warning(
                    "Failed to activate volume endpoint: %s. Volume control disabled.", e
                )

    def change_volume(self, increase: bool, step: float = 0.05) -> float | None:
        """Adjusts the system audio volume.

        Args:
            increase: True to raise volume, False to lower volume.
            step: The change in volume as a percentage scalar (e.g. 0.05 for 5%).

        Returns:
            The new volume level [0.0, 1.0] if successful, or None if failed.
        """
        if not self._is_windows or self._volume_interface is None:
            logger.warning(
                "System volume control not supported or initialized on this platform/configuration."
            )
            return None

        try:
            current_vol = self._volume_interface.GetMasterVolumeLevelScalar()
            delta = step if increase else -step
            new_vol = max(0.0, min(1.0, current_vol + delta))
            self._volume_interface.SetMasterVolumeLevelScalar(new_vol, None)
            logger.info("Volume adjusted to: %d%%", int(new_vol * 100))
            return new_vol
        except Exception as e:
            logger.error("Error setting volume level: %s", e)
            return None

    def fallback_set_brightness(self, percent: int) -> None:
        """Scales brightness via native Windows WMI via PowerShell.

        Args:
            percent: Brightness percentage [0, 100].
        """
        try:
            # Scales brightness via native Windows WMI via PowerShell
            cmd = f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{percent})"
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

    def change_brightness(self, increase: bool, step: int = 5) -> int | None:
        """Adjusts the monitor brightness.

        Args:
            increase: True to raise brightness, False to lower brightness.
            step: The change in brightness percentage (e.g. 5 for 5%).

        Returns:
            The new brightness percentage [0, 100] if successful, or None if failed.
        """
        current_brightness = None

        if SBC_AVAILABLE:
            try:
                brightness_list = sbc.get_brightness()
                if brightness_list:
                    current_brightness = brightness_list[0]
            except Exception as e:
                logger.warning("sbc.get_brightness() failed: %s. Trying fallback.", e)

        # Fallback to query current brightness via PowerShell/WMI if on Windows
        if current_brightness is None and self._is_windows:
            try:
                cmd = "powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if res.returncode == 0 and res.stdout.strip().isdigit():
                    current_brightness = int(res.stdout.strip())
            except Exception as e:
                logger.warning("Fallback query for brightness failed: %s", e)

        # Default fallback value if everything fails
        if current_brightness is None:
            if not hasattr(self, "_current_brightness_cache"):
                self._current_brightness_cache = 50
            current_brightness = self._current_brightness_cache

        delta = step if increase else -step
        new_brightness = max(0, min(100, current_brightness + delta))

        # Try setting using SBC first if available
        sbc_success = False
        if SBC_AVAILABLE:
            try:
                sbc.set_brightness(new_brightness)
                sbc_success = True
                logger.info("Brightness adjusted via SBC to: %d%%", new_brightness)
            except Exception as e:
                logger.warning("sbc.set_brightness() failed: %s. Using Windows PowerShell fallback.", e)

        # Try setting using PowerShell fallback if SBC failed or was unavailable
        if not sbc_success and self._is_windows:
            try:
                self.fallback_set_brightness(new_brightness)
                sbc_success = True
                logger.info("Brightness adjusted via PowerShell fallback to: %d%%", new_brightness)
            except Exception as e:
                logger.error("PowerShell fallback for brightness failed: %s", e)
                return None

        if not sbc_success:
            logger.warning("Brightness control not successful.")
            return None

        self._current_brightness_cache = new_brightness
        return new_brightness
