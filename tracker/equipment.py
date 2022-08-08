from pathlib import Path
import cv2
import mss
import numpy


def screen_capture() -> numpy.ndarray:
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": 3440, "height": 1440}
        capture = numpy.array(sct.grab(monitor), dtype="uint8")
        return cv2.cvtColor(capture, cv2.COLOR_BGR2GRAY)


def find_equipment_in_image(img, template) -> (int, int, int):
    """
    Parses equipment out of an image
    :param img:
    :param template:
    :return:
    """
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img, template, eval('cv2.TM_CCOEFF'))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return max_val, top_left, bottom_right
