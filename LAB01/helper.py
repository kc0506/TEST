from enum import Enum
import threading
from typing import Callable
import cv2
from matplotlib.cbook import print_cycles
import numpy as np


def callback(res):
    return


def createSlider(R_THRES, G_THRES, B_THRES):
    # create a window
    cv2.namedWindow("Threshold Sliders")
    # create a slider
    cv2.createTrackbar("R", "Threshold Sliders", R_THRES, 255, callback)
    cv2.createTrackbar("G", "Threshold Sliders", G_THRES, 255, callback)
    cv2.createTrackbar("B", "Threshold Sliders", B_THRES, 255, callback)


def set_interval(func: Callable, sec: float, is_running: Callable[[], bool]):
    def func_wrapper():
        set_interval(func, sec, is_running)
        func()

    t = threading.Timer(sec, func_wrapper)
    t.start()
    return t


class Colors(Enum):
    """ANSI color codes"""

    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"
    END = "\033[0m"


def printc(color: Colors, s: str):
    print(f"{color.value}{s}{Colors.END.value}")



#######################  Utility  #######################
def put_digit(display, digit: int):
    if digit == None:
        cv2.putText(
            display, f"Current Digit: None", (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2
        )
    else:
        cv2.putText(
            display,
            f"Current Digit: {digit}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2,
        )

def get_euclidean_distance(pos1: tuple, pos2: tuple):
    return (abs(pos1[0]-pos2[0])**2 + abs(pos1[1]-pos2[1])**2)**0.5


# frame: your frame
# path : your save location path
# mode : 0-> No crop, 1-> Crop
# return the path of the screenshot
def screenshot(frame, path:str, mode:int):
	crop_frame = frame[50:480, 0:640]
	cv2.imwrite(path, crop_frame)					# Screenshot current display
	img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
	if(mode == 1): # Crop
		ret, thresh = cv2.threshold(img, 1, 255, cv2.THRESH_BINARY)
		# Find contours in the binary mask
		contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		# Iterate through the contours and find the largest one (assuming the white line is the largest contour)
		largest_contour = max(contours, key=cv2.contourArea)

		# Get the bounding box of the largest contour
		x, y, w, h = cv2.boundingRect(largest_contour)
		center_x = (x + x + w) / 2
		center_y = (y + y + h) / 2
		r = max(w/2, h/2) + 30
		s_x = int(max(0, center_x - r))
		e_x = int(min(480, center_x + r))
		s_y = int(max(50, center_y - r))
		e_y = int(min(640, center_y + r))
		#cropped_image = img[s_y:e_y, s_x:e_x]
		w = max(30, w)
		cropped_image = img[y:y+h, x-30:x+w+30]
		cropped_image = 255 - cropped_image
		cv2.imwrite('./img/cropped_image.png', cropped_image)
		return './img/cropped_image.png'
	return path