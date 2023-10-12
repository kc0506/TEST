from abc import ABC, abstractmethod
import datetime
import threading
from time import sleep
from typing import Callable, Protocol, Sequence
import typing
import cv2

from cv2.typing import MatLike


import datetime

FRAME = 1 / 120
MIN_RADIUS = 20

ContourHandler = Callable[[Sequence[MatLike], float], None]

tick0 = datetime.datetime.now()


@typing.runtime_checkable
class ContoursHandlerClass(Protocol):
    def handle(self, contours: Sequence[MatLike], tick: float):
        pass


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


MIN_TOUCH_PERIOD = 0.05
MIN_NOTOUCH_PERIOD = 0.05
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
