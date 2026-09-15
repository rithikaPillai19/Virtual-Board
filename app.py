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

    # Supported palette cycler
    palette_colors = [
        ("BLUE", (255, 0, 0)),
        ("GREEN", (0, 255, 0)),
        ("RED", (0, 0, 255)),
        ("YELLOW", (0, 255, 255))
    ]
    color_idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Mirror video frame for intuitive interaction
        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = VirtualCanvas(frame.shape)

        frame = detector.find_hands(frame, draw=False)
        hands = detector.get_all_hands(frame)

        left_hand_lms = None
        right_hand_lms = None

        # Sort hands spatially: Left half of camera view = Left Hand; Right half = Right Hand
        for hand in hands:
            wrist_x = hand["lms"][0][1]
            if wrist_x < frame.shape[1] // 2:
                left_hand_lms = hand["lms"]
            else:
                right_hand_lms = hand["lms"]

        # ----------------------------------------------------
        # 1. EVALUATE LEFT HAND STATE (COMMAND DECK)
        # ----------------------------------------------------
        left_mode = "HOVER"  # Default when left hand is at rest / closed

        if left_hand_lms:
            l_fingers = detector.fingers_up(left_hand_lms, "Left")
            l_count = sum(l_fingers)

            # COMMAND: ALL 5 FINGERS UP -> ERASER
            if l_count == 5:
                left_mode = "ERASER"

            # COMMAND: 2 FINGERS UP (Index + Middle) -> COLOR SELECT / PALETTE
            elif l_count == 2 and l_fingers[1] == 1 and l_fingers[2] == 1:
                left_mode = "COLOR_SWITCH"

            # COMMAND: THUMB ONLY UP -> DRAW (PEN DOWN)
            elif l_fingers[0] == 1 and l_fingers[1] == 0 and l_fingers[2] == 0 and l_fingers[3] == 0 and l_fingers[4] == 0:
                left_mode = "DRAW"

            # HUD Display for Left Hand Trigger
            cv2.putText(frame, f"LEFT HAND TRIGGER: {left_mode}", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        else:
            cv2.putText(frame, "LEFT HAND: NOT DETECTED (HOVER)", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 2)

        # ----------------------------------------------------
        # 2. EXECUTE RIGHT HAND POINTER VIA LEFT HAND COMMAND
        # ----------------------------------------------------
        if right_hand_lms:
            # Right Index Finger Tip coordinates (Landmark 8)
            rx, ry = right_hand_lms[8][1], right_hand_lms[8][2]

            # BRANCH 1: ERASER MODE (Left hand has all 5 fingers open)
            if left_mode == "ERASER":
                canvas.erase((rx, ry))
                cv2.circle(frame, (rx, ry), canvas.eraser_radius, (0, 0, 255), 2)
                cv2.putText(frame, "STATUS: ERASING", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # BRANCH 2: COLOR SWITCH MODE (Left hand shows 2 fingers)
            elif left_mode == "COLOR_SWITCH":
                canvas.reset_point()
                cv2.circle(frame, (rx, ry), 12, (255, 255, 255), cv2.FILLED)
                cv2.circle(frame, (rx, ry), 14, (0, 0, 0), 2)

                # Tap any button on top bar to switch directly
                if ry < 70:
                    action = ui.check_interaction((rx, ry))
                    if action == "CLEAR":
                        canvas.clear()
                    elif action is not None:
                        canvas.current_color = action

                cv2.putText(frame, "STATUS: COLOR SWITCH (TAP TOP BAR)", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

            # BRANCH 3: DRAW MODE (Left hand thumb is UP)
            elif left_mode == "DRAW":
                canvas.draw_stroke((rx, ry))
                cv2.circle(frame, (rx, ry), 8, canvas.current_color, cv2.FILLED)
                cv2.putText(frame, "STATUS: DRAWING", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, canvas.current_color, 2)

            # BRANCH 4: FREE HOVER (Left hand closed, resting, or not active)
            else:
                canvas.reset_point()
                cv2.circle(frame, (rx, ry), 6, (0, 255, 255), 2)
                cv2.putText(frame, "STATUS: AIMING / HOVER (IDLE)", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

        else:
            if canvas:
                canvas.reset_point()

        # Merge drawing canvas and render UI palette
        output = canvas.merge(frame)
        ui.draw_palette(output)

        cv2.imshow("Virtual Screen Board - Two-Hand Control", output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()