
import math
from typing import Callable
import cv2
from cv2.typing import MatLike
import numpy as np

from processor import UnitouchHandler


TRAJECTORY_WIDTH = 20
TRAJECTORY_DELAY = 2
MIN_DIST = 5
MAX_DIST = 50


class TrajectoryHandler(UnitouchHandler):
    frame: MatLike
    offset: tuple[int, int] | None = None
    last_touch_end: float | None = None
    shape: tuple[int, ...]

    def __init__(self, shape: tuple[int, ...], callback: Callable[[], bool]) -> None:
        self.shape = shape
        self.frame = np.zeros(shape)

    def get_frame(self):
        return self.frame

    def touch(
        self,
        x: float,
        y: float,
        tick: float,
    ):
        x = int(x)
        y = int(y)
        if self.offset is None:
            self.offset = x, y
            return

        x0, y0 = self.offset
        dist = (x - x0) ** 2 + (y - y0) ** 2
        dist = math.isqrt(dist)
        if dist > MAX_DIST or dist < MIN_DIST:
            pass
        else:
            cv2.line(self.frame, self.offset, (x, y), (255, 255, 255), TRAJECTORY_WIDTH)
        self.offset = x, y
        self.last_touch_end = None

    def notouch(self, tick: float):
        self.offset = None

        if self.last_touch_end:
            if tick - self.last_touch_end >= TRAJECTORY_DELAY:
                self.frame[:] = 0
                self.last_touch_end = None
            else:
                pass
        else:
            self.last_touch_end = tick
