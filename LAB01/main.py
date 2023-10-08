import signal
import sys
import cv2
from cv2.typing import MatLike
from pyscreeze import center
from digit_recognization import recognize_img_to_digit, train_model
from gesture import GestureHandler, Processor, TrajectoryHandler

from helper import *


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
R_THRES = 160
G_THRES = 0
B_THRES = 130

#######################  Function  #######################

cur_contours = None


def get_cur_contours():
    return cur_contours


def signal_handler(signum, frame):
    print("teminating...")
    if signum == signal.SIGINT.value:
        if processor:
            processor.kill_loop()
        sys.exit(1)


signal.signal(signal.SIGINT, signal_handler)


def filter_frame(frame: MatLike):
    b, g, r = cv2.split(frame)

    r_thres = cv2.getTrackbarPos("R", "Threshold Sliders")
    g_thres = cv2.getTrackbarPos("G", "Threshold Sliders")
    b_thres = cv2.getTrackbarPos("B", "Threshold Sliders")
    _, r = cv2.threshold(r, r_thres, 255, cv2.THRESH_BINARY)
    _, g = cv2.threshold(g, g_thres, 255, cv2.THRESH_BINARY)
    _, b = cv2.threshold(b, b_thres, 255, cv2.THRESH_BINARY)

    not_b = cv2.bitwise_not(b, mask=None)
    result = cv2.bitwise_and(r, not_b, mask=None)
    return result


if __name__ == "__main__":
    CLF_MODEL = train_model()  # Get Model

    processor = Processor(get_cur_contours)
    processor.register_handler(GestureHandler())
    processor.main_loop()

    cap = cv2.VideoCapture(CAMERA)
    createSlider(R_THRES, G_THRES, B_THRES)

    cur_digit = None
    trajectory_handler = None
    DIGIT_IMG = "./img/digit.png"

    def get_digit():
        if trajectory_handler:
            path_cropped = screenshot(trajectory_handler.frame, DIGIT_IMG, 1)  # Screenshot
            if path_cropped:
                global cur_digit
                cur_digit = recognize_img_to_digit(path_cropped, CLF_MODEL, False)  # Get Result

    set_interval(get_digit, 0.5, lambda: processor.running)

    while True:
        ret, frame = cap.read()
        if FLIP_HORIZONTAL:
            frame = cv2.flip(frame, 1)

        if trajectory_handler is None:
            trajectory_handler = TrajectoryHandler(frame.shape, lambda: processor.running)
            processor.register_handler(trajectory_handler)

        result = filter_frame(frame)

        # Find and draw contours
        contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cur_contours = contours

        display = cv2.cvtColor(result, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(display, contours, -1, (0, 0, 255))
        put_digit(display, cur_digit)

        # Show the frame
        cv2.imshow("frame", frame)
        cv2.imshow("display", display)
        cv2.imshow("trajectory", trajectory_handler.frame)

        # Press h to toggle horizontal flip
        # Press q to quit
        key = cv2.waitKey(1) & 0xFF
        if key == ord("h"):
            FLIP_HORIZONTAL = not FLIP_HORIZONTAL
        elif key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
