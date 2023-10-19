from abc import ABC, abstractmethod
from dataclasses import dataclass
from io import RawIOBase
import math
import random
import cv2
from matplotlib.pylab import rand
import numpy as np
from typing import Sequence
from cv2.typing import MatLike

from helper import get_euclidean_distance
from logger import Logger


AREA_THRES = 100


@dataclass
class Finger:
    x: int
    y: int
    id: int

    @property
    def pos(self):
        return (self.x, self.y)


TIMEOUT = 1
MAX_FINGERS = 5
MAX_FINGER_DIST = 70


class MultitouchHandler(ABC):
    @abstractmethod
    def update(self, new_fingers: dict[int, Finger], tick: float):
        raise NotImplementedError

    @abstractmethod
    def clear_finger(self, id: int):
        raise NotImplementedError

    id_pool: set[int]
    fingers: dict[int, Finger] = dict()
    last_finger_st: dict[int, float]

    # last_notouch_st: float | None = None

    def __init__(self) -> None:
        self.id_pool = set(i for i in range(MAX_FINGERS))
        # print(self.id_pool)
        self.last_finger_st = dict()

    def handle(self, contours: Sequence[MatLike], tick: float):
        contours = tuple(filter(lambda cnt: cv2.contourArea(cnt) > AREA_THRES, contours))
        # print("\nfingers: ", self.fingers)
        # print("pool: ", self.id_pool)
        # print("last_st: ", self.last_finger_st)

        for id, t in self.last_finger_st.items():
            if tick - t > TIMEOUT:
                # assert id in self.fingers
                if id in self.fingers:
                    self.fingers.pop(id)
                self.id_pool.add(id)
                self.clear_finger(id)

        for id in self.id_pool:
            if id in self.last_finger_st:
                self.last_finger_st.pop(id)

        if len(contours) == 0:  # No input
            # if self.last_notouch_st is None:
            #     self.last_notouch_st = tick
            # elif tick - self.last_notouch_st < TIMEOUT:
            #     self.clear()
            pass
        else:
            # print("len: ", len(contours))
            matched_ids = set()
            new_fingers: dict[int, Finger] = {}
            for cnt in contours:
                # Calculate the area of the contour
                # Find the centroid
                (x, y), radius = cv2.minEnclosingCircle(cnt)
                x, y = int(x), int(y)
                radius = int(radius)

                # * First try to match existing finger
                matched_id = None
                cur_dist = MAX_FINGER_DIST
                for finger in self.fingers.values():
                    if finger.id in matched_ids:
                        continue
                    dist = get_euclidean_distance(finger.pos, (x, y))
                    if dist <= cur_dist:
                        matched_id = finger.id

                # print(matched_id)
                if matched_id is not None:
                    matched_ids.add(matched_id)
                    new_fingers[matched_id] = Finger(x, y, matched_id)
                else:
                    if not self.id_pool:
                        # print(self.fingers)
                        raise Exception("too many fingers!")
                    new_id = self.id_pool.pop()
                    # print(f"pop {new_id}")
                    finger = Finger(x, y, new_id)
                    new_fingers[finger.id] = finger

            # print("new: ", new_fingers)
            for finger in new_fingers.values():
                self.last_finger_st[finger.id] = tick

            self.update(new_fingers, tick)
            self.fingers = new_fingers
            # for id, finger in new_fingers.items():
            #     self.fingers[id] = finger


COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
# COLORS = tuple(tuple(random.randint(100, 255) for _ in range(3)) for _ in range(MAX_FINGERS))
LINE_WIDTH = 20


class MultiTrajectory(MultitouchHandler):
    frame: MatLike
    finger_trails: dict[int, list[tuple[int, int]]] = dict()

    def __init__(self, shape: tuple[int, ...]) -> None:
        self.frame = np.zeros(shape)
        for i in range(MAX_FINGERS):
            self.finger_trails[i] = []
        super().__init__()

    def clear_finger(self, id: int):
        trails = self.finger_trails[id]
        for i in range(len(trails) - 1):
            cv2.line(self.frame, trails[i], trails[i + 1], (0, 0, 0), LINE_WIDTH)
        self.finger_trails[id].clear()

    def update(self, new_fingers: dict[int, Finger], tick: float):
        for finger in new_fingers.values():
            id = finger.id
            color = COLORS[hash(id) % len(COLORS)]
            if id in self.fingers:
                cv2.line(self.frame, self.fingers[id].pos, finger.pos, color, LINE_WIDTH)

            self.finger_trails[id].append(finger.pos)


ZOOM_THRES = 1.05
ROTATE_THRES = 2 / 180 * math.pi

MULTI_TIMEOUT = 1


class MultiGesture(MultitouchHandler):
    logger = Logger()

    length: float | None = None
    slope: float | None = None
    last_update: float | None = None

    def __init__(self) -> None:
        super().__init__()

    def update(self, new_fingers: dict[int, Finger], tick: float):
        if len(new_fingers) < 2:
            if self.last_update:
                if tick - self.last_update > MULTI_TIMEOUT:
                    self.last_update = None
                    self.length = None
                    self.slope = None
            return

        self.last_update = tick
        f1, f2 = tuple(new_fingers.values())[:2]

        new_length = get_euclidean_distance(f1.pos, f2.pos)
        new_slope = math.inf if f1.x == f2.x else (f2.y - f1.y) / (f2.x - f1.x)

        ratio = new_length / self.length if self.length else 1
        theta = math.atan(new_slope)
        theta0 = math.atan(self.slope) if self.slope else theta

        self.length = new_length
        self.slope = new_slope

        # print(ratio, (theta-theta0)/math.pi*180)

        flag = False
        if ratio >= ZOOM_THRES:
            self.logger.log("zoom in")
            flag = True
        elif ratio <= 1 / ZOOM_THRES:
            self.logger.log("zoom out")
            flag = True
        elif theta - theta0 >= ROTATE_THRES:
            self.logger.log("rotate clockwise")
            flag = True
        elif theta - theta0 <= -ROTATE_THRES:
            self.logger.log("rotate counter-clockwise")
            flag = True
        if flag:
            self.slope = new_slope
            self.length = new_length

    def clear_finger(self, id: int):
        # return super().clear_finger(id)
        pass
