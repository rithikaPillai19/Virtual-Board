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

        # Sort detected hands based on screen position (after mirror flip)
        # Left side of screen = your left hand; Right side = your right hand
        for hand in hands:
            wrist_x = hand["lms"][0][1]
            if wrist_x < frame.shape[1] // 2:
                left_hand_lms = hand["lms"]
            else:
                right_hand_lms = hand["lms"]

        # Evaluate Clutch Switch (Left Hand Thumb UP)
        left_clutch_engaged = False
        if left_hand_lms:
            left_fingers = detector.fingers_up(left_hand_lms, "Left")
            # Thumb tip is higher than thumb knuckle
            if len(left_fingers) > 0 and left_fingers[0] == 1:
                left_clutch_engaged = True
                cv2.putText(frame, "TRIGGER: ACTIVE (PEN DOWN)", (20, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                cv2.putText(frame, "TRIGGER: STANDBY", (20, 140),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

        # Evaluate Drawing / Erasing / Selection (Right Hand)
        if right_hand_lms:
            rx, ry = right_hand_lms[8][1], right_hand_lms[8][2]   # Right Index Tip
            r_palm_x, r_palm_y = right_hand_lms[9][1], right_hand_lms[9][2]
            right_fingers = detector.fingers_up(right_hand_lms, "Right")

            # MODE 1: WHOLE RIGHT HAND OPEN -> ERASER
            if sum(right_fingers) >= 4:
                canvas.erase((r_palm_x, r_palm_y))
                cv2.circle(frame, (r_palm_x, r_palm_y), canvas.eraser_radius, (0, 0, 255), 2)
                cv2.putText(frame, "MODE: ERASER", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # MODE 2: RIGHT INDEX + MIDDLE UP -> COLOR SELECTION (TOP BAR)
            elif len(right_fingers) >= 3 and right_fingers[1] == 1 and right_fingers[2] == 1:
                canvas.reset_point()
                cv2.circle(frame, (rx, ry), 10, (200, 200, 200), cv2.FILLED)
                if ry < 70:
                    action = ui.check_interaction((rx, ry))
                    if action == "CLEAR":
                        canvas.clear()
                    elif action is not None:
                        canvas.current_color = action
                cv2.putText(frame, "MODE: COLOR SELECT", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)

            # MODE 3: RIGHT INDEX UP + LEFT CLUTCH ENGAGED -> DRAW
            elif len(right_fingers) >= 2 and right_fingers[1] == 1 and left_clutch_engaged:
                canvas.draw_stroke((rx, ry))
                cv2.circle(frame, (rx, ry), 8, canvas.current_color, cv2.FILLED)
                cv2.putText(frame, "MODE: DRAWING", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, canvas.current_color, 2)

            # MODE 4: RIGHT INDEX UP WITHOUT CLUTCH -> FREE HOVER / AIM
            elif len(right_fingers) >= 2 and right_fingers[1] == 1:
                canvas.reset_point()
                cv2.circle(frame, (rx, ry), 6, (0, 255, 255), 2)
                cv2.putText(frame, "MODE: AIMING (HOLD LEFT THUMB UP TO INK)", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            else:
                canvas.reset_point()
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