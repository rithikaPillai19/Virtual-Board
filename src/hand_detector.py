import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self, max_hands=2, detection_con=0.75, track_con=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

    def find_hands(self, frame, draw=False):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return frame

    def get_all_hands(self, frame):
        """Returns a list of dicts: [{'label': 'Left'/'Right', 'lms': [(id, x, y), ...]}, ...]"""
        all_hands = []
        if self.results and self.results.multi_hand_landmarks and self.results.multi_handedness:
            h, w, _ = frame.shape
            for handedness, hand_landmarks in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                # MediaPipe handedness is inverted relative to mirrored webcam
                label = handedness.classification[0].label  # 'Left' or 'Right'
                lm_list = []
                for lm_id, lm in enumerate(hand_landmarks.landmark):
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lm_list.append((lm_id, cx, cy))
                all_hands.append({"label": label, "lms": lm_list})
        return all_hands

    def fingers_up(self, lm_list, hand_label="Right"):
        if len(lm_list) < 21:
            return []

        fingers = []

        # Thumb up / extended detection
        # Checks if thumb tip (4) is higher (smaller Y) than its IP joint (3)
        if lm_list[4][2] < lm_list[3][2]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 fingers: check if tip Y is strictly higher than PIP joint Y
        for i in range(1, 5):
            if lm_list[self.tip_ids[i]][2] < lm_list[self.tip_ids[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers