"""
Air Flower Draw
----------------
A small webcam prototype: pinch your thumb and index finger together and
move your hand in the air — a trail of flowers gets drawn on screen,
following your fingertip. Change the flower color with number keys.

Controls:
    1-8   -> change flower color (see COLOR_NAMES below)
    c     -> clear the canvas
    s     -> save a screenshot to ./screenshots/
    q/ESC -> quit

How "drawing" works:
    Pinch your thumb tip and index fingertip together (like a pinch
    gesture) to put the "pen" down. Move your hand while pinching to
    draw a trail of flowers. Release the pinch to lift the pen.

Requirements:
    pip install -r requirements.txt
    (needs a working webcam)
"""

import math
import os
import time

import cv2
import mediapipe as mp
import numpy as np

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

CAM_INDEX = 0                # change if you have multiple cameras
FRAME_W, FRAME_H = 960, 720
PINCH_THRESHOLD = 40         # pixels; smaller = must pinch tighter
MIN_FLOWER_SPACING = 26      # min pixel distance between two flowers on a trail
FLOWER_SIZE = 16

# BGR colors (OpenCV uses Blue-Green-Red order, not RGB)
COLORS = {
    ord('1'): (60, 60, 255),    # red
    ord('2'): (0, 140, 255),    # orange
    ord('3'): (0, 230, 255),    # yellow
    ord('4'): (90, 200, 90),    # green
    ord('5'): (255, 140, 60),   # blue
    ord('6'): (220, 80, 200),   # purple
    ord('7'): (200, 120, 255),  # pink
    ord('8'): (245, 245, 245),  # white
}
COLOR_NAMES = {
    ord('1'): "Red", ord('2'): "Orange", ord('3'): "Yellow",
    ord('4'): "Green", ord('5'): "Blue", ord('6'): "Purple",
    ord('7'): "Pink", ord('8'): "White",
}

# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------

def draw_flower(canvas, center, color, size=FLOWER_SIZE):
    """Draw a simple flower (petals + center dot) onto canvas at `center`."""
    cx, cy = center

    # petals: circles arranged around the center
    for angle_deg in range(0, 360, 60):
        rad = math.radians(angle_deg)
        px = int(cx + size * math.cos(rad))
        py = int(cy + size * math.sin(rad))
        cv2.circle(canvas, (px, py), max(size // 2, 6), color, -1, cv2.LINE_AA)

    # center dot, contrasting color so it reads as a flower center
    center_color = (255, 255, 255) if color != (0, 230, 255) else (40, 40, 40)
    cv2.circle(canvas, (cx, cy), max(size // 3, 4), center_color, -1, cv2.LINE_AA)


def dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1,
        min_detection_confidence=0.7,
        min_tracking_confidence=0.6,
    )

    cap = cv2.VideoCapture(CAM_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_H)

    if not cap.isOpened():
        print("Could not open webcam. Check CAM_INDEX or camera permissions.")
        return

    canvas = None  # created once we know the frame size
    current_color_key = ord('1')
    last_flower_point = None
    pen_down = False

    os.makedirs("screenshots", exist_ok=True)

    print("Air Flower Draw running. Focus the window and press 'q' to quit.")

    while True:
        ok, frame = cap.read()
        if not ok:
            print("Failed to read from webcam.")
            break

        frame = cv2.flip(frame, 1)  # mirror, feels natural
        h, w = frame.shape[:2]

        if canvas is None:
            canvas = np.zeros((h, w, 3), dtype=np.uint8)

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        pen_down = False
        fingertip_px = None

        if result.multi_hand_landmarks:
            hand_landmarks = result.multi_hand_landmarks[0]
            lm = hand_landmarks.landmark

            index_tip = (int(lm[8].x * w), int(lm[8].y * h))
            thumb_tip = (int(lm[4].x * w), int(lm[4].y * h))
            fingertip_px = index_tip

            pinch_dist = dist(index_tip, thumb_tip)
            pen_down = pinch_dist < PINCH_THRESHOLD

            # visual feedback: show fingertip + thumb + pinch line
            cv2.circle(frame, index_tip, 8, (0, 255, 0), -1)
            cv2.circle(frame, thumb_tip, 8, (0, 200, 255), -1)
            line_color = (0, 255, 0) if pen_down else (100, 100, 100)
            cv2.line(frame, index_tip, thumb_tip, line_color, 2)

        color = COLORS[current_color_key]

        if pen_down and fingertip_px is not None:
            if last_flower_point is None or dist(fingertip_px, last_flower_point) >= MIN_FLOWER_SPACING:
                draw_flower(canvas, fingertip_px, color)
                last_flower_point = fingertip_px
        else:
            last_flower_point = None  # lifted pen, start a fresh stroke next time

        # composite: show canvas flowers over the live camera feed
        mask = canvas.any(axis=2)
        composite = frame.copy()
        composite[mask] = canvas[mask]

        # HUD
        cv2.rectangle(composite, (0, 0), (w, 40), (30, 30, 30), -1)
        status = "PEN DOWN (pinch)" if pen_down else "pen up - pinch thumb+index to draw"
        cv2.putText(composite, f"Color: {COLOR_NAMES[current_color_key]}   {status}",
                    (10, 27), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.circle(composite, (w - 25, 20), 12, color, -1)
        cv2.putText(composite, "1-8 color | c clear | s save | q quit",
                    (10, h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1, cv2.LINE_AA)

        cv2.imshow("Air Flower Draw", composite)

        key = cv2.waitKey(1) & 0xFF
        if key in COLORS:
            current_color_key = key
        elif key == ord('c'):
            canvas[:] = 0
        elif key == ord('s'):
            fname = f"screenshots/air_flowers_{int(time.time())}.png"
            cv2.imwrite(fname, composite)
            print(f"Saved {fname}")
        elif key == ord('q') or key == 27:  # 'q' or ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
