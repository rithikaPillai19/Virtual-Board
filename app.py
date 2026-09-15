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

    # Available drawing colors to cycle through
    palette = [
        ("BLUE", (255, 0, 0)),
        ("GREEN", (0, 255, 0)),
        ("RED", (0, 0, 255)),
        ("YELLOW", (0, 255, 255))
    ]
    color_index = 0

    # Debounce / cooldown control for color switching
    last_switch_time = 0.0
    switch_cooldown = 0.6  # Minimum seconds between switches
    was_in_switch_pose = False

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = VirtualCanvas(frame.shape)
            canvas.current_color = palette[color_index][1]

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
            current_time = time.time()

            # COMMAND 1: ALL 4 OR 5 FINGERS UP -> ERASER
            if sum(l_fingers) >= 4:
                left_mode = "ERASER"
                was_in_switch_pose = False

            # COMMAND 2: INDEX + MIDDLE UP, RING + PINKY DOWN -> COLOR SWITCH
            # (Loosened thumb check: thumb can be tucked or relaxed)
            elif l_fingers[1] == 1 and l_fingers[2] == 1 and l_fingers[3] == 0 and l_fingers[4] == 0:
                left_mode = "COLOR_SWITCH"
                
                # Single-shot trigger with cooldown
                if not was_in_switch_pose and (current_time - last_switch_time > switch_cooldown):
                    color_index = (color_index + 1) % len(palette)
                    canvas.current_color = palette[color_index][1]
                    last_switch_time = current_time
                    was_in_switch_pose = True

            # COMMAND 3: THUMB UP, ALL 4 FINGERS DOWN -> DRAW
            elif l_fingers[0] == 1 and sum(l_fingers[1:]) == 0:
                left_mode = "DRAW"
                was_in_switch_pose = False

            else:
                was_in_switch_pose = False

            # Status HUD
            color_name = palette[color_index][0]
            cv2.putText(frame, f"LEFT: {left_mode} | COLOR: {color_name}", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 2)
        else:
            was_in_switch_pose = False
            cv2.putText(frame, "LEFT HAND: NOT DETECTED (HOVER)", (20, 140),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (180, 180, 180), 2)

        # ----------------------------------------------------
        # 2. EXECUTE RIGHT HAND POINTER
        # ----------------------------------------------------
        if right_hand_lms:
            rx, ry = right_hand_lms[8][1], right_hand_lms[8][2]

            if left_mode == "ERASER":
                canvas.erase((rx, ry))
                cv2.circle(frame, (rx, ry), canvas.eraser_radius, (0, 0, 255), 2)
                cv2.putText(frame, "MODE: ERASING", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            elif left_mode == "COLOR_SWITCH":
                canvas.reset_point()
                # Pulse visual confirmation around pointer
                cv2.circle(frame, (rx, ry), 12, canvas.current_color, cv2.FILLED)
                cv2.circle(frame, (rx, ry), 15, (255, 255, 255), 2)
                cv2.putText(frame, f"SWITCHED TO {palette[color_index][0]}", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, canvas.current_color, 2)

            elif left_mode == "DRAW":
                canvas.draw_stroke((rx, ry))
                cv2.circle(frame, (rx, ry), 8, canvas.current_color, cv2.FILLED)
                cv2.putText(frame, "MODE: DRAWING", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, canvas.current_color, 2)

            else:
                canvas.reset_point()
                cv2.circle(frame, (rx, ry), 6, (0, 255, 255), 2)
                cv2.putText(frame, "MODE: HOVER", (20, 100),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
        else:
            if canvas:
                canvas.reset_point()

        output = canvas.merge(frame)
        ui.draw_palette(output)

        cv2.imshow("Virtual Screen Board - Two-Hand Control", output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()