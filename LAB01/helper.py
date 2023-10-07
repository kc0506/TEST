import threading
from typing import Callable
import cv2
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


class Colors:
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
