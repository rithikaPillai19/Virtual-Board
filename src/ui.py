import cv2

class BoardUI:
    def __init__(self):
        self.buttons = [
            {"label": "CLEAR", "rect": (20, 10, 120, 65), "color": (180, 180, 180), "val": "CLEAR"},
            {"label": "BLUE",  "rect": (140, 10, 240, 65), "color": (255, 0, 0), "val": (255, 0, 0)},
            {"label": "GREEN", "rect": (260, 10, 360, 65), "color": (0, 255, 0), "val": (0, 255, 0)},
            {"label": "RED",   "rect": (380, 10, 480, 65), "color": (0, 0, 255), "val": (0, 0, 255)},
            {"label": "YELLOW","rect": (500, 10, 600, 65), "color": (0, 255, 255), "val": (0, 255, 255)},
        ]

    def draw_palette(self, frame):
        for btn in self.buttons:
            x1, y1, x2, y2 = btn["rect"]
            cv2.rectangle(frame, (x1, y1), (x2, y2), btn["color"], -1)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            cv2.putText(frame, btn["label"], (x1 + 10, y1 + 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

    def check_interaction(self, point):
        px, py = point
        for btn in self.buttons:
            x1, y1, x2, y2 = btn["rect"]
            if x1 <= px <= x2 and y1 <= py <= y2:
                return btn["val"]
        return None