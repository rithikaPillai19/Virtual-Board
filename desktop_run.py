import cv2
import time
from src.hand_detector import HandTracker
from src.canvas import VirtualCanvas
from src.ui import BoardUI

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = HandTracker(max_hands=2, detection_con=0.8, track_con=0.8)
    ui = BoardUI()
    canvas = None

    # Persistent Locked State
    locked_mode = "HOVER"  # Initial state: HOVER, DRAW, ERASER, COLOR_SELECT
    last_switch_time = 0.0
    switch_cooldown = 0.5   # Cooldown to avoid rapid fluttering

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = VirtualCanvas(frame.shape)

        frame = detector.find_hands(frame, draw=False)
        hands = detector.get_all_hands(frame)

        left_hand_lms = None
        right_hand_lms = None

        # Sort hands spatially: Left side of mirrored screen = Left Hand
        for hand in hands:
            wrist_x = hand["lms"][0][1]
            if wrist_x < frame.shape[1] // 2:
                left_hand_lms = hand["lms"]
            else:
                right_hand_lms = hand["lms"]

        current_time = time.time()

        # ----------------------------------------------------
        # 1. EVALUATE LEFT HAND & UPDATE LOCKED STATE
        # ----------------------------------------------------
        if left_hand_lms and (current_time - last_switch_time > switch_cooldown):
            l_fingers = detector.fingers_up(left_hand_lms, "Left")
            l_count = sum(l_fingers)

            # 1. ALL 5 FINGERS OPEN -> LOCK ERASER
            if l_count >= 4 and locked_mode != "ERASER":
                locked_mode = "ERASER"
                last_switch_time = current_time
                canvas.reset_point()

            # 2. THUMB + INDEX + MIDDLE UP -> LOCK COLOR SELECT
            elif l_fingers[0] == 1 and l_fingers[1] == 1 and l_fingers[2] == 1 and l_fingers[3] == 0 and l_fingers[4] == 0:
                if locked_mode != "COLOR_SELECT":
                    locked_mode = "COLOR_SELECT"
                    last_switch_time = current_time
                    canvas.reset_point()

            # 3. THUMB ONLY UP -> LOCK DRAW
            elif l_fingers[0] == 1 and sum(l_fingers[1:]) == 0:
                if locked_mode != "DRAW":
                    locked_mode = "DRAW"
                    last_switch_time = current_time
                    canvas.reset_point()

            # 4. CLOSED FIST (0 FINGERS) -> LOCK HOVER / PAUSE
            elif l_count == 0 and locked_mode != "HOVER":
                locked_mode = "HOVER"
                last_switch_time = current_time
                canvas.reset_point()

        # ----------------------------------------------------
        # 2. EXECUTE RIGHT HAND POINTER IN CURRENT LOCKED STATE
        # ----------------------------------------------------
        if right_hand_lms:
            rx, ry = right_hand_lms[8][1], right_hand_lms[8][2]

            if locked_mode == "ERASER":
                canvas.erase((rx, ry))
                cv2.circle(frame, (rx, ry), canvas.eraser_radius, (0, 0, 255), 2)
                cv2.putText(frame, "ACTIVE: ERASER", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            elif locked_mode == "COLOR_SELECT":
                canvas.reset_point()
                cv2.circle(frame, (rx, ry), 12, (255, 255, 255), cv2.FILLED)
                cv2.circle(frame, (rx, ry), 15, (0, 0, 0), 2)

                # Tap top-right buttons
                if ry <= 70:
                    action = ui.check_interaction((rx, ry))
                    if action == "CLEAR":
                        canvas.clear()
                    elif action is not None:
                        canvas.current_color = action

                cv2.putText(frame, "ACTIVE: SELECT COLOR (TAP TOP-RIGHT)", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            elif locked_mode == "DRAW":
                canvas.draw_stroke((rx, ry))
                cv2.circle(frame, (rx, ry), 8, canvas.current_color, cv2.FILLED)
                cv2.putText(frame, "ACTIVE: DRAWING", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, canvas.current_color, 2)

            else:  # HOVER MODE
                canvas.reset_point()
                cv2.circle(frame, (rx, ry), 6, (0, 255, 255), 2)
                cv2.putText(frame, "ACTIVE: HOVER / AIM (PAUSED)", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

        else:
            if canvas:
                canvas.reset_point()

        # Render Telemetry HUD
        hand_status = "DETECTED" if left_hand_lms else "DOWN / RESTING"
        cv2.putText(frame, f"LOCKED MODE: {locked_mode}", (20, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, f"LEFT HAND: {hand_status}", (20, 170),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)

        output = canvas.merge(frame)
        ui.draw_palette(output)

        cv2.imshow("Virtual Screen Board - Air Canvas (Locked Modes)", output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()