import datetime
from enum import Enum
import threading
from time import sleep
from typing import Callable, Sequence
import cv2

from cv2.typing import MatLike

from helper import Colors, printc, set_interval


TICK = 0.01
TOUCH_DELAY_SEC = 0.1
NOTOUCH_DELAY_SEC = 0.1
TOUCH_DELAY = 30
NOTOUCH_DELAY = 30

CLICK_PERIOD = 100
MIN_RADIUS = 10
CLICK_DELAY = 30


class Direction(Enum):
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


class GestureHandler:
    get_cur_contours: Callable[[], Sequence[MatLike] | None]
    running = True
    tick = 0

    def __init__(self, get_cur_contours: Callable[[], Sequence[MatLike] | None]) -> None:
        self.get_cur_contours = get_cur_contours

    def kill_loop(self):
        self.running = False

    prev = datetime.datetime.now()

    def main_loop(self):
        def loop_target():
            while self.running:
                contours = self.get_cur_contours()
                if contours:
                    self.handle_contours(contours)
                sleep(TICK)
                self.tick += 1

        t = threading.Thread(target=loop_target)
        t.start()

    touch_start_tick = -1
    notouch_start_tick = -1

    print_longtap = False
    direction: Direction = Direction.NONE
    drag_offset: tuple[float, float] | None = None

    def handle_contours(self, contours: Sequence[MatLike]):
        contours = tuple(filter(lambda cnt: cv2.minEnclosingCircle(cnt)[1] >= MIN_RADIUS, contours))
        contours = sorted(contours, key=lambda cnt: cv2.minEnclosingCircle(cnt)[1])
        flag = bool(contours)

        if flag:
            self.notouch_start_tick = -1

            if self.touch_start_tick == -1:
                self.touch_start_tick = self.tick
            delta = self.tick - self.touch_start_tick

            if delta >= CLICK_PERIOD:
                if not self.print_longtap:
                    printc(Colors.BLUE, "[+] long tap")
                    self.print_longtap = True

                (x, y), _ = cv2.minEnclosingCircle(contours[-1])
                if self.drag_offset:
                    x0, y0 = self.drag_offset

                    if abs(x0 - x) > 20:
                        # print(f"new: {(x, y)}")
                        # print(f"delta: {x-x0}")
                        new_direction = Direction.RIGHT if x0 < x else Direction.LEFT
                        if new_direction != self.direction:
                            print(f"[+] swipe {new_direction.value}")

                        self.drag_offset = (x, y)
                        self.direction = new_direction
                else:
                    self.drag_offset = (x, y)
                    # print(f"offset: {(x, y)}")

        else:
            if self.notouch_start_tick == -1:
                self.notouch_start_tick = self.tick
            delta = self.tick - self.notouch_start_tick
            if delta < NOTOUCH_DELAY:
                return

            if self.touch_start_tick != -1:
                if self.tick - self.touch_start_tick >= CLICK_PERIOD:
                    printc(Colors.RED, "[+] long tap end")
                elif delta >= CLICK_DELAY:
                    printc(Colors.GREEN, "[+] tap")

            self.direction = Direction.NONE
            self.drag_offset = None
            self.print_longtap = False
            self.touch_start_tick = -1
