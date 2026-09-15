import cv2
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

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror video frame for natural interaction
        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = VirtualCanvas(frame.shape)

        frame = detector.find_hands(frame, draw=False)
        hands = detector.get_all_hands(frame)

        left_hand_lms = None
        right_hand_lms = None

        # Sort hands spatially: Left half of screen = Left Hand; Right half = Right Hand
        for hand in hands:
            wrist_x = hand["lms"][0][1]
            if wrist_x < frame.shape[1] // 2:
                left_hand_lms = hand["lms"]
            else:
                right_hand_lms = hand["lms"]

        # ----------------------------------------------------
        # 1. EVALUATE LEFT HAND STATE (COMMAND DECK)
        # ----------------------------------------------------
        left_mode = "HOVER"

        if left_hand_lms:
            l_fingers = detector.fingers_up(left_hand_lms, "Left")
            l_count = sum(l_fingers)

            # COMMAND 1: ALL 4 OR 5 FINGERS UP -> ERASER MODE
            if l_count >= 4:
                left_mode = "ERASER"

            # COMMAND 2: THUMB + INDEX + MIDDLE UP (Ring & Pinky DOWN) -> COLOR SELECTION UNLOCK
            elif l_fingers[0] == 1 and l_fingers[1] == 1 and l_fingers[2] == 1 and l_fingers[3] == 0 and l_fingers[4] == 0:
                left_mode = "COLOR_SELECT"

            # COMMAND 3: ONLY THUMB UP (All other fingers DOWN) -> DRAW MODE
            elif l_fingers[0] == 1 and l_fingers[1] == 0 and l_fingers[2] == 0 and l_fingers[3] == 0 and l_fingers[4] == 0:
                left_mode = "DRAW"

            # HUD Display for Left Hand State
            cv2.putText(frame, f"LEFT COMMAND: {left_mode}", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "LEFT COMMAND: NONE (HOVER)", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 2)

        # ----------------------------------------------------
        # 2. EXECUTE RIGHT HAND POINTER (STYLUS)
        # ----------------------------------------------------
        if right_hand_lms:
            # Right index fingertip coordinates (Landmark 8)
            rx, ry = right_hand_lms[8][1], right_hand_lms[8][2]

            # BRANCH 1: ERASER (Left hand open palm)
            if left_mode == "ERASER":
                canvas.erase((rx, ry))
                cv2.circle(frame, (rx, ry), canvas.eraser_radius, (0, 0, 255), 2)
                cv2.putText(frame, "MODE: ERASING", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # BRANCH 2: COLOR SELECTION (Left hand: Thumb + 2 Fingers UP)
            elif left_mode == "COLOR_SELECT":
                canvas.reset_point()
                # Draw targeting selector reticle
                cv2.circle(frame, (rx, ry), 12, (255, 255, 255), cv2.FILLED)
                cv2.circle(frame, (rx, ry), 15, (0, 0, 0), 2)

                # Tap any color button on the top toolbar
                if ry <= 70:
                    action = ui.check_interaction((rx, ry))
                    if action == "CLEAR":
                        canvas.clear()
                    elif action is not None:
                        canvas.current_color = action

                cv2.putText(frame, "MODE: SELECT COLOR (POINT AT TOP BAR)", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            # BRANCH 3: DRAW MODE (Left hand: Thumb ONLY UP)
            elif left_mode == "DRAW":
                canvas.draw_stroke((rx, ry))
                cv2.circle(frame, (rx, ry), 8, canvas.current_color, cv2.FILLED)
                cv2.putText(frame, "MODE: DRAWING", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, canvas.current_color, 2)

            # BRANCH 4: IDLE / HOVER
            else:
                canvas.reset_point()
                cv2.circle(frame, (rx, ry), 6, (0, 255, 255), 2)
                cv2.putText(frame, "MODE: HOVER / AIM", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

        else:
            if canvas:
                canvas.reset_point()

        output = canvas.merge(frame)
        ui.draw_palette(output)

        cv2.imshow("Virtual Screen Board - Air Canvas", output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()