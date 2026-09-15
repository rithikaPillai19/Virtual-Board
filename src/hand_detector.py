import cv2
import mediapipe as mp
import numpy as np


class HandTracker:
    def __init__(self, max_hands=1, detection_con=0.75, track_con=0.7):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_hands,
            min_detection_confidence=detection_con,
            min_tracking_confidence=track_con
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.tip_ids = [4, 8, 12, 16, 20]  # Thumb, Index, Middle, Ring, Pinky

    def find_hands(self, frame, draw=True):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks and draw:
            for hand_lms in self.results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(frame, hand_lms, self.mp_hands.HAND_CONNECTIONS)
        return frame

    def get_landmarks(self, frame):
        lm_list = []
        if self.results and self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[0]
            h, w, _ = frame.shape
            for lm_id, lm in enumerate(my_hand.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append((lm_id, cx, cy))
        return lm_list

    def fingers_up(self, lm_list):
        if len(lm_list) < 21:
            return []

        fingers = []

        # Thumb: Calculate Euclidean distance relative to palm width
        thumb_tip = np.array([lm_list[4][1], lm_list[4][2]], dtype=np.float32)
        index_mcp = np.array([lm_list[5][1], lm_list[5][2]], dtype=np.float32)
        pinky_mcp = np.array([lm_list[17][1], lm_list[17][2]], dtype=np.float32)
        
        palm_width = np.linalg.norm(index_mcp - pinky_mcp)
        thumb_dist = np.linalg.norm(thumb_tip - index_mcp)

        # Safety check for palm scale
        if palm_width > 0 and (thumb_dist / palm_width) > 0.45:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other 4 Fingers: Check if tip Y is strictly higher (smaller Y value) than PIP joint Y
        for i in range(1, 5):
            if lm_list[self.tip_ids[i]][2] < lm_list[self.tip_ids[i] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers