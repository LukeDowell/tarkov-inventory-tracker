import json
import tkinter as tk
from pathlib import Path

import cv2
import mss
import numpy

script_path = Path(__file__).parent
item_json_path = (script_path / '../data/items.json').resolve()
temp_dir = (script_path / '../data/template').resolve()
ui_files = [t for t in (temp_dir / 'UI').iterdir() if t.is_file() and t.name.endswith("png")]
ui_templates = list(map(lambda f: (f.name, cv2.imread(f.as_posix(), flags=cv2.IMREAD_GRAYSCALE)), ui_files))


def screen_capture() -> numpy.ndarray:
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": int(sct.monitors[1]['width'] / 2), "height": 1440}
        capture = numpy.array(sct.grab(monitor), dtype="uint8")
        return cv2.cvtColor(capture, cv2.COLOR_RGB2GRAY)


def template_match(img, temp):
    res = cv2.matchTemplate(img, temp, eval('cv2.TM_CCOEFF'))
    return cv2.minMaxLoc(res)


if __name__ == "__main__":
    # img = cv2.imread("../tests/stash-screenshot-gear.png")
    # y = 200
    # x = 200
    # h = 400
    # w = 400
    # crop_img = img[y:y+h, x:x+w].copy()
    # cv2.imshow("cropped", crop_img)
    # cv2.waitKey(0)

    window = tk.Tk()
    canvas = tk.Canvas(window, bg="white", width=3440, height=1400)
    label = tk.Label(window, bg="white")

    window.wm_attributes("-topmost", True)
    window.wm_attributes("-fullscreen", True)
    window.wm_attributes("-disabled", True)
    window.wm_attributes("-transparentcolor", "white")
    window.config(bg="white")

    with open(item_json_path) as item_json_file:
        data = json.load(item_json_file)

    ui_files = [t for t in (temp_dir / 'UI').iterdir() if t.is_file() and t.name.endswith("png")]
    ui_templates = list(map(lambda f: (f.name, cv2.imread(f.as_posix(), flags=cv2.IMREAD_GRAYSCALE)), ui_files))

    while "Capturing Screen":
        screen = screen_capture()
        canvas.delete('all')
        detected_objects = []

        for name, template in ui_templates:
            w, h, *d = template.shape[::-1]
            min_val, max_val, min_loc, max_loc = template_match(screen, template)
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            if max_val > 5_500_000:
                detected_objects.append((name, top_left, bottom_right))

        for o in detected_objects:
            top_left = o[1]
            bottom_right = o[2]
            canvas.create_text(top_left[0] + 50, top_left[1] - 15, text=o[0], fill="red", font='Helvetica 12 bold')
            canvas.create_rectangle(top_left[0], top_left[1], bottom_right[0], bottom_right[1])

        canvas.pack(fill=tk.BOTH)
        window.update()
