from abc import ABC, abstractmethod
import datetime
import dis
from math import inf
import math
import threading
from time import sleep
from typing import Callable, Protocol, Sequence
import typing
import cv2

from cv2.typing import MatLike
import numpy as np

from helper import Colors, printc
from logger import Logger
from processor import Processor, UnitouchHandler


# * Time constants (sec)
FRAME = 1 / 120

MIN_TOUCH_PERIOD = 0.05
MIN_NOTOUCH_PERIOD = 0.05

MAX_TAP_PERIOD = 0.5
MAX_DOUBLE_TAP_DELAY = 0.5

# * Image constants
MIN_RADIUS = 20
MIN_SHIFT = 40


class Direction:
    dir: str

    def __init__(self, x, y) -> None:
        self.dir = ((("none", "none"), ("none", "none")), (("left", "right"), ("up", "down")))[
            max(abs(x), abs(y)) >= MIN_SHIFT
        ][abs(x) < abs(y)][(abs(x) > abs(y) and x > 0) or (abs(y) > abs(x) and y > 0)]

        if self.dir == "none":
            self.dir = ""

    def __repr__(self) -> str:
        return self.dir


logger = Logger()

# logger.log(["move", "right"])
# logger.log("move")
# logger.log(["move", ""])
# logger.log('rotate')
# logger.log(["move", "left"])


class GestureHandler(UnitouchHandler):
    """
    This handler classify touch events by the following:
    1) tap/ long tap: whether delta between touch and notouch <= MAX_TAP_PERIOD
    2) tap/ double tap: whether time after last tap >= MAX_DOUBLE_TAP_DELAY

    Thus there are 4 groups:
    1) tap
    2) long tap
    3) double tap
    4) double long tap
    """

    cur_touch_st = -1
    last_touch_end = -1

    drag_offset: tuple[float, float] | None = None

    logging: bool = True

    def log(self, payload: str | tuple[str, ...]):
        if self.logging:
            logger.log(payload)

    def on_double_tap(self):
        # self.logging = not self.logging
        # if self.logging:
        #     print("logging on")
        # else:
        #     print("logging off")
        pass

    def touch(self, x: float, y: float, tick: float):
        if self.cur_touch_st == -1:
            self.cur_touch_st = tick
            return

        delta = tick - self.cur_touch_st
        delay = self.cur_touch_st - self.last_touch_end if self.last_touch_end != -1 else inf
        if delta > MAX_TAP_PERIOD:
            if delay <= MAX_DOUBLE_TAP_DELAY:
                tap_type = "double long tap"

            else:
                tap_type = "long tap"
            self.log(tap_type)

            if self.drag_offset is None:
                self.drag_offset = (x, y)
                return
            x0, y0 = self.drag_offset
            direction = Direction(x - x0, y - y0)
            if direction.dir != "":
                self.log((tap_type, str(direction)))
                self.drag_offset = x, y

        else:
            pass

    def notouch(self, tick: float):
        if self.cur_touch_st == -1:
            return

        delta = tick - self.cur_touch_st
        delay = self.cur_touch_st - self.last_touch_end if self.last_touch_end != -1 else inf
        if delta <= MAX_TAP_PERIOD:
            if delay <= MAX_DOUBLE_TAP_DELAY:
                tap_type = "double tap"
                self.on_double_tap()
            else:
                tap_type = "tap"
            self.log(tap_type)

        self.drag_offset = None
        self.cur_touch_st = -1
        self.last_touch_end = tick


class GUIHandler(UnitouchHandler):
    ...
