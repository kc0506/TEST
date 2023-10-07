from abc import ABC, abstractmethod
import datetime
from enum import Enum
from math import inf
import threading
from time import sleep
from typing import Callable, List, Protocol, Sequence
import cv2

from cv2.typing import MatLike
from numpy import logaddexp
from yarg import latest_updated_packages

from helper import Colors, printc


# * Time constants (sec)
FRAME = 1 / 120

MIN_TOUCH_PERIOD = 0.1
MIN_NOTOUCH_PERIOD = 0.1

MAX_TAP_PERIOD = 0.4
MAX_DOUBLE_TAP_DELAY = 0.4

# * Image constants
MIN_RADIUS = 10
MIN_SHIFT = 20


class Direction:
    dir: str

    def __init__(self, x, y) -> None:
        self.dir = ((("none", "none"), ("none", "none")), (("left", "right"), ("down", "up")))[
            max(abs(x), abs(y)) >= MIN_SHIFT
        ][abs(x) < abs(y)][(abs(x) > abs(y) and x > 0) or (abs(y) > abs(x) and y > 0)]

        if self.dir == "none":
            self.dir = ""

    def __repr__(self) -> str:
        return self.dir


class ContoursHandler(Protocol):
    def handle(self, contours: Sequence[MatLike], tick: float):
        pass


tick0 = datetime.datetime.now()


class Processor:
    get_cur_contours: Callable[[], Sequence[MatLike] | None]
    running = True
    handlers: list[ContoursHandler] = []

    def __init__(self, get_cur_contours: Callable[[], Sequence[MatLike] | None]) -> None:
        self.get_cur_contours = get_cur_contours

    def kill_loop(self):
        self.running = False

    def main_loop(self):
        def loop_target():
            while self.running:
                contours = self.get_cur_contours()
                cur_time = datetime.datetime.now() - tick0
                cur_time = cur_time.total_seconds()

                if contours is None:
                    continue

                contours = tuple(
                    filter(lambda cnt: cv2.minEnclosingCircle(cnt)[1] < MIN_RADIUS, contours)
                )

                for hanlder in self.handlers:
                    hanlder.handle(contours, cur_time)

                sleep(FRAME)

        t = threading.Thread(target=loop_target)
        t.start()

    def register_handler(self, handler: ContoursHandler):
        self.handlers.append(handler)


class UnitouchHandler(ABC):
    """
    Abstract class that only handle contour with largest radius.
    Handle single point touch event.
    """

    last_touch_st = -1
    last_notouch_st = -1

    @abstractmethod
    def touch(self, x: float, y: float, tick: float):
        raise NotImplementedError

    @abstractmethod
    def notouch(self, tick: float):
        raise NotImplementedError

    def handle(self, contours: Sequence[MatLike], tick: float):
        if contours:
            cnt = sorted(contours, key=lambda cnt: cv2.minEnclosingCircle(cnt)[1])[-1]

            # touch
            if self.last_touch_st != -1:
                delta = tick - self.last_touch_st
                if delta >= MIN_TOUCH_PERIOD:
                    x, y = cv2.minEnclosingCircle(cnt)[0]
                    self.touch(x, y, tick)
            else:
                self.last_touch_st = tick

            # ? 對 touch 比較寬容
            self.last_notouch_st = -1
        else:
            # no touch
            if self.last_notouch_st != -1:
                delta = tick - self.last_notouch_st
                if delta >= MIN_NOTOUCH_PERIOD:
                    self.last_touch_st = -1
                    self.notouch(tick)
            else:
                self.last_notouch_st = tick


class Logger:
    colors = [Colors.BLUE, Colors.RED, Colors.GREEN, Colors.CYAN, Colors.YELLOW]

    state: str | List[str] = "default"

    def log(self, payload: str | list[str]):
        if payload == self.state:
            return

        if type(payload) == str:
            color = self.colors[hash(payload) % len(self.colors)]
            log = "[+] " + payload
        else:
            color = self.colors[hash(payload[0]) % len(self.colors)]
            log = ""
            if (type(self.state) != list and self.state != payload[0]) and payload[0] != self.state[
                0
            ]:
                log = f"[+] {payload[0]}"

            s = " ".join(payload[1:])
            if s:
                log += ("\n" if log else "") + "    " + s

        if log:
            printc(color, log)
        self.state = payload


logger = Logger()

# logger.log("move")
# logger.log(["move", "right"])
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

    def touch(self, x: float, y: float, tick: float):
        if self.cur_touch_st == -1:
            self.cur_touch_st = tick
            return

        delta = tick - self.cur_touch_st
        delay = self.cur_touch_st - self.last_touch_end if self.last_touch_end != -1 else inf
        if delta > MAX_TAP_PERIOD:
            if delay > MAX_DOUBLE_TAP_DELAY:
                tap_type = "double long tap"
            else:
                tap_type = "long tap"
            logger.log(tap_type)

            if self.drag_offset is None:
                self.drag_offset = (x, y)
                return
            x0, y0 = self.drag_offset
            direction = Direction(x - x0, y - y0)
            logger.log([tap_type, str(direction)])
        else:
            pass

    def notouch(self, tick: float):
        if self.cur_touch_st == -1:
            return

        delta = tick - self.cur_touch_st
        delay = self.cur_touch_st - self.last_touch_end if self.last_touch_end != -1 else inf
        if delta > MAX_TAP_PERIOD:
            if delay > MAX_DOUBLE_TAP_DELAY:
                tap_type = "double tap"
            else:
                tap_type = "tap"
            logger.log(tap_type)

        self.drag_offset = None
        self.cur_touch_st = -1
        self.last_touch_end = tick
