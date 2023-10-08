from abc import ABC, abstractmethod
import datetime
from math import inf
import threading
from time import sleep
from typing import Callable, Protocol, Sequence
import typing
import cv2

from cv2.typing import MatLike
import numpy as np

from helper import Colors, printc


# * Time constants (sec)
FRAME = 1 / 120

MIN_TOUCH_PERIOD = 0.05
MIN_NOTOUCH_PERIOD = 0.05

MAX_TAP_PERIOD = 0.5
MAX_DOUBLE_TAP_DELAY = 0.5

# * Image constants
MIN_RADIUS = 40
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


@typing.runtime_checkable
class ContoursHandlerClass(Protocol):
    def handle(self, contours: Sequence[MatLike], tick: float):
        pass


ContourHandler = Callable[[Sequence[MatLike], float], None]


tick0 = datetime.datetime.now()


class Processor:
    get_cur_contours: Callable[[], Sequence[MatLike] | None]
    running = True
    handlers: list[ContoursHandlerClass | ContourHandler] = []

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
                    filter(lambda cnt: cv2.minEnclosingCircle(cnt)[1] >= MIN_RADIUS, contours)
                )

                for hanlder in self.handlers:
                    if isinstance(hanlder, ContoursHandlerClass):
                        hanlder.handle(contours, cur_time)
                    else:
                        hanlder(contours, cur_time)

                sleep(FRAME)

        t = threading.Thread(target=loop_target)
        t.start()

    def register_handler(self, handler: ContoursHandlerClass | ContourHandler):
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
        # print(len( contours ))
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

            # ? More tolerate for touch - cancel potential notouch on any touch
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

    state: str | tuple[str, ...] = "default"

    def log(self, payload: str | tuple[str, ...]):
        if payload == self.state:
            return
        log = ""

        if type(payload) == str:
            color = self.colors[hash(payload) % len(self.colors)]
            if type(self.state) != tuple or self.state[0] != payload:
                log = "[+] " + payload
                self.state = payload
        else:
            color = self.colors[hash(payload[0]) % len(self.colors)]
            if (type(self.state) != tuple and self.state != payload[0]) and payload[
                0
            ] != self.state[0]:
                log = f"[+] {payload[0]}"

            s = " ".join(payload[1:])
            if s:
                log += ("\n" if log else "") + "    " + s

            self.state = payload

        if log:
            printc(color, log)


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
        self.logging = not self.logging
        if self.logging:
            print("logging on")
        else:
            print("logging off")

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


TRAJECTORY_WIDTH = 20
TRAJECTORY_DELAY = 2


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


# Processor(lambda: None).register_handler(TrajectoryHandler())
# Processor(lambda: None).register_handler(GestureHandler())
