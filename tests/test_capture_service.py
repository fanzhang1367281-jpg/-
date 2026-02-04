import unittest
from unittest.mock import MagicMock, patch

from backend.capture.platform.windows import WindowsCaptureService


class DummyImage:
    def __init__(self, width: int, height: int) -> None:
        self.shape = (height, width, 3)


class TestWindowsCaptureService(unittest.TestCase):
    def test_bind_window(self) -> None:
        service = WindowsCaptureService()
        rect = {"left": 0, "top": 0, "width": 800, "height": 600}
        with patch.object(service, "_find_window", return_value=(1234, rect)):
            bound = service.bind_window("GG Poker")
        self.assertTrue(bound)
        info = service.get_window_info()
        self.assertEqual(info["window_handle"], 1234)
        self.assertEqual(info["window_rect"], rect)

    def test_capture_frame(self) -> None:
        service = WindowsCaptureService()
        service._window_rect = {"left": 0, "top": 0, "width": 640, "height": 480}
        service._window_handle = 4321
        service._window_title = "GG Poker"
        dummy_image = DummyImage(640, 480)
        with patch.object(service, "_grab_region", return_value=dummy_image):
            frame = service.capture_frame()
        self.assertIsNotNone(frame)
        assert frame is not None
        self.assertEqual(frame.width, 640)
        self.assertEqual(frame.height, 480)
        self.assertEqual(frame.metadata["window_handle"], 4321)

    def test_roi_crop(self) -> None:
        service = WindowsCaptureService()
        service._window_rect = {"left": 10, "top": 20, "width": 400, "height": 300}
        service._window_handle = 111
        service.set_roi(5, 10, 200, 100)
        dummy_image = DummyImage(200, 100)
        grab_mock = MagicMock(return_value=dummy_image)
        with patch.object(service, "_grab_region", grab_mock):
            frame = service.capture_frame()
        self.assertIsNotNone(frame)
        grab_mock.assert_called_once_with(
            {"left": 15, "top": 30, "width": 200, "height": 100}
        )


if __name__ == "__main__":
    unittest.main()
