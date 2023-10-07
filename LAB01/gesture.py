import datetime
import threading
from time import sleep
from typing import Callable, Sequence
import cv2


from cv2.typing import MatLike

from helper import Colors, set_interval


TICK = 0.01
TOUCH_DELAY_SEC = 0.1
NOTOUCH_DELAY_SEC = 0.1
TOUCH_DELAY = 30
NOTOUCH_DELAY = 30

CLICK_PERIOD = 200
MIN_RADIUS = 5
CLICK_DELAY = 30


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

    def handle_contours(self, contours: Sequence[MatLike]):
        flag = False
        if contours:
            cnt = contours[0]
            (x, y), radius = cv2.minEnclosingCircle(cnt)
            flag = radius >= MIN_RADIUS
            if flag:
                print("radius: ", radius)

        if flag:
            print("touch")
            self.notouch_start_tick = -1

            if self.touch_start_tick == -1:
                self.touch_start_tick = self.tick
            delta = self.tick - self.touch_start_tick
            if delta >= CLICK_PERIOD:
                print(f"{Colors.BLUE}[+] long tap{Colors.END}")
            print(self.tick, self.touch_start_tick)

        else:
            if self.notouch_start_tick == -1:
                self.notouch_start_tick = self.tick
            delta = self.tick - self.notouch_start_tick
            if delta < NOTOUCH_DELAY:
                return

            # print("notouch: ", delta)
            if self.touch_start_tick != -1:
                if delta >= CLICK_PERIOD:
                    print(f"{Colors.RED}[+] long tap end{Colors.END}")
                elif delta >= CLICK_DELAY:
                    print(f"{Colors.GREEN}[+] tap{Colors.END}")

            self.touch_start_tick = -1
