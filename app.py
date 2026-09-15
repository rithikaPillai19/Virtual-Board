import cv2
from src.hand_detector import HandTracker
from src.canvas import VirtualCanvas
from src.ui import BoardUI

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    detector = HandTracker(detection_con=0.8, track_con=0.8)
    ui = BoardUI()
    canvas = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip frame horizontally for mirror view
        frame = cv2.flip(frame, 1)

        if canvas is None:
            canvas = VirtualCanvas(frame.shape)

        frame = detector.find_hands(frame, draw=False)
        lm_list = detector.get_landmarks(frame)

        if len(lm_list) != 0:
            # Landmark 8: Index finger tip, Landmark 12: Middle finger tip
            x1, y1 = lm_list[8][1], lm_list[8][2]
            x2, y2 = lm_list[12][1], lm_list[12][2]
            # Landmark 9: Middle of palm for eraser centroid
            px, py = lm_list[9][1], lm_list[9][2]

            fingers = detector.fingers_up(lm_list)
            cv2.putText(frame, f"Fingers: {fingers}", (20, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

            # MODE 1: Whole hand open (Eraser)
            if sum(fingers) >= 4:
                canvas.erase((px, py))
                cv2.circle(frame, (px, py), canvas.eraser_radius, (0, 0, 255), 2)
                cv2.putText(frame, "ERASER MODE", (20, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

            # MODE 2: Selection / Hover (Index + Middle UP)
            elif len(fingers) >= 3 and fingers[1] == 1 and fingers[2] == 1:
                canvas.reset_point()
                cv2.circle(frame, (x1, y1), 10, (200, 200, 200), cv2.FILLED)
                if y1 < 70:
                    action = ui.check_interaction((x1, y1))
                    if action == "CLEAR":
                        canvas.clear()
                    elif action is not None:
                        canvas.current_color = action
                cv2.putText(frame, "SELECTION MODE", (20, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)

            # MODE 3: Drawing (Index UP, Middle DOWN)
            elif len(fingers) >= 3 and fingers[1] == 1 and fingers[2] == 0:
                canvas.draw_stroke((x1, y1))
                cv2.circle(frame, (x1, y1), 10, canvas.current_color, cv2.FILLED)
                cv2.putText(frame, "DRAW MODE", (20, 110),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, canvas.current_color, 2)
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