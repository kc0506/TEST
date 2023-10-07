import signal
import sys
import cv2
import numpy as np
from gesture import GestureHandler

from helper import *

# from digit_recognization import *


#######################  Constant  #######################

CAMERA = 1

# FILEPATH
digit_img = "./img/digit.png"

# List to store positions
positions = []

# BOOLEAN
FLIP_HORIZONTAL = True  # Flag to control horizontal flip


# THRESHOLD
AREA_THRES = 100
R_THRES = 180
G_THRES = 0
B_THRES = 130

#######################  Function  #######################

cur_contours = None


def get_cur_contours():
    return cur_contours


def signal_handler(signum, frame):
    print("teminating...")
    if signum == signal.SIGINT.value:
        if gesture_handler:
            gesture_handler.kill_loop()
        sys.exit(1)


signal.signal(signal.SIGINT, signal_handler)


#######################  Main      #######################

if __name__ == "__main__":
    gesture_handler = GestureHandler(get_cur_contours)
    gesture_handler.main_loop()

    cap = cv2.VideoCapture(CAMERA)
    createSlider(R_THRES, G_THRES, B_THRES)

    while True:
        # Get one frame from the camera
        ret, frame = cap.read()

        # Check if horizontal flip is enabled
        if FLIP_HORIZONTAL:
            frame = cv2.flip(frame, 1)

        try:
            # Split RGB channels
            b, g, r = cv2.split(frame)
        except:
            continue

        # Perform thresholding to each channel
        r_thres = cv2.getTrackbarPos("R", "Threshold Sliders")
        g_thres = cv2.getTrackbarPos("G", "Threshold Sliders")
        b_thres = cv2.getTrackbarPos("B", "Threshold Sliders")
        _, r = cv2.threshold(r, r_thres, 255, cv2.THRESH_BINARY)
        _, g = cv2.threshold(g, g_thres, 255, cv2.THRESH_BINARY)
        _, b = cv2.threshold(b, b_thres, 255, cv2.THRESH_BINARY)

        # Get the final result using bitwise operation
        not_b = cv2.bitwise_not(b, mask=None)
        result = cv2.bitwise_and(r, not_b, mask=None)

        # Find and draw contours
        contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        display = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(display, contours, -1, (0, 0, 255))

        cur_contours = contours
        # if contours:

        # print(len(contours))
        #     radius = cv2.minEnclosingCircle(contours[0])[1]
        #     print(radius)

        # Iterate through each contour, check the area and find the center

        for cnt in contours:
            # Calculate the area of the contour
            area = cv2.contourArea(cnt)
            if area > AREA_THRES:
                # Find the centroid
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                center = (int(x), int(y))
                radius = int(radius)
                cv2.circle(display, center, radius, (0, 255, 0), 2)
                cv2.circle(display, center, 2, (0, 255, 0), -1)
                cv2.putText(
                    display,
                    f"({center[0]}, {center[1]})",
                    (center[0] + radius, center[1] + radius),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )

                # Add the object's position to the history list
                positions.append(center)

        # # Draw the object's trajectory
        # for i in range(1, len(positions)):
        # 	cv2.line(display, positions[i - 1], positions[i], (255, 255, 255), 5)

        # Show the frame
        cv2.imshow("frame", frame)
        cv2.imshow("display", display)

        # Press h to toggle horizontal flip
        # Press c to clear
        # Press q to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord("h"):
            FLIP_HORIZONTAL = not FLIP_HORIZONTAL
        elif key == ord("c"):
            positions = []
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
