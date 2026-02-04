"""Capture module exports."""
from backend.capture.service import CaptureService, Frame
from backend.capture.platform.windows import WindowsCaptureService


def create_capture_service() -> CaptureService:
    """Factory for capture service based on platform."""
    import platform

    system = platform.system().lower()
    if system == "windows":
        return WindowsCaptureService()
    raise NotImplementedError(f"Capture service not implemented for {system}")


__all__ = ["CaptureService", "Frame", "WindowsCaptureService", "create_capture_service"]
