"""Windows capture service implementation."""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Tuple

from backend.capture.service import CaptureService, Frame

logger = logging.getLogger(__name__)


class WindowsCaptureService(CaptureService):
    """Windows implementation of capture service."""

    def __init__(self) -> None:
        super().__init__()
        self._window_handle: Optional[int] = None
        self._window_rect: Optional[Dict[str, int]] = None
        self._window_title: Optional[str] = None

    def bind_window(self, window_title: str) -> bool:
        """Bind to the first window matching the title.

        Args:
            window_title: Window title to match.

        Returns:
            True when a window is bound.
        """
        try:
            handle, rect = self._find_window(window_title)
        except Exception:
            logger.exception("Failed to bind window: %s", window_title)
            return False

        if handle is None or rect is None:
            logger.warning("No window found for title: %s", window_title)
            return False

        self._window_handle = handle
        self._window_rect = rect
        self._window_title = window_title
        return True

    def capture_frame(self) -> Optional[Frame]:
        """Capture a single frame from the bound window."""
        if self._window_rect is None:
            logger.warning("No window bound, cannot capture")
            return None

        region = self._window_rect.copy()
        if self._roi is not None:
            region = self._apply_roi(region, self._roi)
            if region is None:
                logger.warning("ROI outside window bounds")
                return None

        try:
            image = self._grab_region(region)
        except Exception:
            logger.exception("Failed to capture frame")
            return None

        metadata = {
            "window_title": self._window_title,
            "window_handle": self._window_handle,
            "window_rect": self._window_rect,
            "roi": self._roi,
        }
        return self._build_frame(image=image, metadata=metadata)

    def get_window_info(self) -> Dict[str, Any]:
        """Return metadata about the bound window."""
        return {
            "window_title": self._window_title,
            "window_handle": self._window_handle,
            "window_rect": self._window_rect,
            "roi": self._roi,
        }

    def _find_window(self, title: str) -> Tuple[Optional[int], Optional[Dict[str, int]]]:
        import pygetwindow as gw
        import win32gui

        windows = gw.getWindowsWithTitle(title)
        if not windows:
            return None, None
        window = windows[0]
        handle = window._hWnd
        rect = win32gui.GetWindowRect(handle)
        window_rect = {
            "left": rect[0],
            "top": rect[1],
            "width": rect[2] - rect[0],
            "height": rect[3] - rect[1],
        }
        return handle, window_rect

    def _apply_roi(
        self, region: Dict[str, int], roi: Tuple[int, int, int, int]
    ) -> Optional[Dict[str, int]]:
        x, y, width, height = roi
        if x + width > region["width"] or y + height > region["height"]:
            return None
        return {
            "left": region["left"] + x,
            "top": region["top"] + y,
            "width": width,
            "height": height,
        }

    def _grab_region(self, region: Dict[str, int]):
        import cv2
        import mss
        import numpy as np
        from PIL import Image

        with mss.mss() as sct:
            screenshot = sct.grab(region)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        img_np = np.array(img)
        return cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
