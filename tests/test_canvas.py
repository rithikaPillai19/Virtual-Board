import os
import sys

# Suppress absl / MediaPipe / TensorFlow C++ logs before importing CV modules
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import unittest
import numpy as np
from src.canvas import VirtualCanvas
from src.ui import BoardUI
from src.hand_detector import HandTracker

class TestVirtualScreenBoard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Instantiate detector once to avoid re-initializing graph per test."""
        cls.detector = HandTracker(max_hands=2, detection_con=0.7, track_con=0.7)

    def setUp(self):
        self.frame_shape = (720, 1280, 3)
        self.canvas = VirtualCanvas(self.frame_shape)
        self.ui = BoardUI()

    def test_canvas_initialization(self):
        """Verify canvas allocates with matching dimensions and initial zeros."""
        self.assertEqual(self.canvas.canvas.shape, self.frame_shape)
        self.assertEqual(np.sum(self.canvas.canvas), 0)

    def test_stroke_rasterization(self):
        """Verify drawing interpolated strokes changes pixel matrix values."""
        self.canvas.draw_stroke((200, 200))
        self.canvas.draw_stroke((250, 250))
        self.assertGreater(np.sum(self.canvas.canvas), 0)

    def test_canvas_clear(self):
        """Verify clear resets all canvas pixel intensities back to 0."""
        self.canvas.draw_stroke((150, 150))
        self.canvas.clear()
        self.assertEqual(np.sum(self.canvas.canvas), 0)

    def test_alpha_blend_compositing(self):
        """Verify blending outputs an image of identical shape and uint8 type."""
        dummy_camera_feed = np.full(self.frame_shape, 128, dtype=np.uint8)
        self.canvas.draw_stroke((300, 300))
        blended = self.canvas.merge(dummy_camera_feed)
        self.assertEqual(blended.shape, self.frame_shape)
        self.assertEqual(blended.dtype, np.uint8)

    def test_reset_point(self):
        """Verify pen lift clears previous coordinate to prevent drag trails."""
        self.canvas.draw_stroke((100, 100))
        self.assertIsNotNone(self.canvas.prev_point)
        self.canvas.reset_point()
        self.assertIsNone(self.canvas.prev_point)

    def test_ui_button_collision(self):
        """Verify button hitboxes on the top-right toolbar."""
        blue_click = (820, 35)
        action = self.ui.check_interaction(blue_click)
        self.assertEqual(action, (255, 0, 0))

        empty_click = (100, 500)
        self.assertIsNone(self.ui.check_interaction(empty_click))

    def test_finger_up_classification(self):
        """Verify fingers_up logic using synthetic landmark points."""
        mock_landmarks = [[i, 500, 500] for i in range(21)]
        mock_landmarks[6] = [6, 500, 300]   # Index PIP
        mock_landmarks[8] = [8, 500, 200]   # Index Tip (UP)
        mock_landmarks[10] = [10, 520, 300]; mock_landmarks[12] = [12, 520, 350]
        mock_landmarks[14] = [14, 540, 300]; mock_landmarks[16] = [16, 540, 350]
        mock_landmarks[18] = [18, 560, 300]; mock_landmarks[20] = [20, 560, 350]
        mock_landmarks[3] = [3, 450, 400];   mock_landmarks[4] = [4, 460, 400]

        fingers = self.detector.fingers_up(mock_landmarks, "Left")
        self.assertEqual(fingers[1], 1)
        self.assertEqual(fingers[2], 0)

if __name__ == "__main__":
    unittest.main(verbosity=2)