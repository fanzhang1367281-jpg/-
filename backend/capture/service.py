"""Capture service base classes and utilities."""
from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class Frame:
    """Container for captured frame data."""

    frame_id: str
    ts_capture: float
    ts_service: float
    image: "Any"
    width: int
    height: int
    metadata: Dict[str, Any] = field(default_factory=dict)


class CaptureService:
    """Base class for window capture services."""

    def __init__(self) -> None:
        self._roi: Optional[Tuple[int, int, int, int]] = None

    def bind_window(self, window_title: str) -> bool:
        """Bind to a target window title.

        Args:
            window_title: Window title to match.

        Returns:
            True if a window is bound.
        """
        raise NotImplementedError

    def set_roi(self, x: int, y: int, width: int, height: int) -> None:
        """Set ROI relative to the window.

        Args:
            x: Left offset.
            y: Top offset.
            width: ROI width.
            height: ROI height.
        """
        if width <= 0 or height <= 0:
            raise ValueError("ROI width and height must be positive")
        if x < 0 or y < 0:
            raise ValueError("ROI coordinates must be non-negative")
        self._roi = (x, y, width, height)

    def capture_frame(self) -> Optional[Frame]:
        """Capture a single frame.

        Returns:
            Frame instance or None if capture failed.
        """
        raise NotImplementedError

    def capture_stream(self, callback: Callable[[Frame], None], fps: int = 30) -> None:
        """Continuously capture frames.

        Args:
            callback: Callback invoked for each frame.
            fps: Target frames per second.
        """
        if fps <= 0:
            raise ValueError("FPS must be positive")
        interval = 1.0 / fps
        logger.info("Starting capture stream at %s FPS", fps)
        while True:
            start = time.perf_counter()
            frame = self.capture_frame()
            if frame is not None:
                callback(frame)
            elapsed = time.perf_counter() - start
            sleep_time = max(0.0, interval - elapsed)
            if sleep_time:
                time.sleep(sleep_time)

    def get_window_info(self) -> Dict[str, Any]:
        """Return window metadata."""
        raise NotImplementedError

    def _build_frame(self, image: Any, metadata: Dict[str, Any]) -> Frame:
        ts_capture = time.perf_counter() * 1000
        ts_service = time.perf_counter() * 1000
        height, width = image.shape[:2]
        return Frame(
            frame_id=str(uuid.uuid4()),
            ts_capture=ts_capture,
            ts_service=ts_service,
            image=image,
            width=width,
            height=height,
            metadata=metadata,
        )
