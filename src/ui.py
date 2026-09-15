import cv2

class BoardUI:
    def __init__(self):
        # Position buttons on the top-right corner of a 1280px-wide canvas
        # 5 buttons of width 110px and gap 10px, starting from x=660 to x=1260
        self.buttons = [
            {"label": "CLEAR",  "rect": (660,  10, 770,  65), "color": (180, 180, 180), "val": "CLEAR"},
            {"label": "BLUE",   "rect": (780,  10, 890,  65), "color": (255, 0, 0),     "val": (255, 0, 0)},
            {"label": "GREEN",  "rect": (900,  10, 1010, 65), "color": (0, 255, 0),     "val": (0, 255, 0)},
            {"label": "RED",    "rect": (1020, 10, 1130, 65), "color": (0, 0, 255),     "val": (0, 0, 255)},
            {"label": "YELLOW", "rect": (1140, 10, 1250, 65), "color": (0, 255, 255),   "val": (0, 255, 255)},
        ]

    def draw_palette(self, frame):
        for btn in self.buttons:
            x1, y1, x2, y2 = btn["rect"]
            # Fill rectangle with button color
            cv2.rectangle(frame, (x1, y1), (x2, y2), btn["color"], -1)
            # White border
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
            # Label
            cv2.putText(frame, btn["label"], (x1 + 12, y1 + 38),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 0), 2)

    def check_interaction(self, point):
        """Returns action or color if the given (x, y) point hits a button."""
        px, py = point
        for btn in self.buttons:
            x1, y1, x2, y2 = btn["rect"]
            if x1 <= px <= x2 and y1 <= py <= y2:
                return btn["val"]
        return None