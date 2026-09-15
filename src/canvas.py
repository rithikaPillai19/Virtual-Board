import cv2
import numpy as np

class VirtualCanvas:
    def __init__(self, shape):
        self.canvas = np.zeros(shape, dtype=np.uint8)
        self.current_color = (255, 0, 0) # Default: Blue
        self.brush_thickness = 7
        self.eraser_radius = 50
        self.prev_point = None

    def draw_stroke(self, point):
        if self.prev_point is None:
            self.prev_point = point
        cv2.line(self.canvas, self.prev_point, point, self.current_color, self.brush_thickness)
        self.prev_point = point

    def erase(self, point):
        # Erase strokes by drawing black circles on the canvas layer
        cv2.circle(self.canvas, point, self.eraser_radius, (0, 0, 0), -1)
        self.prev_point = None

    def reset_point(self):
        self.prev_point = None

    def clear(self):
        self.canvas.fill(0)
        self.prev_point = None

    def merge(self, frame):
        # Create a mask of the canvas
        gray = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2GRAY)
        _, inv_mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY_INV)
        frame_bg = cv2.bitwise_and(frame, frame, mask=inv_mask)
        combined = cv2.add(frame_bg, self.canvas)
        return combined