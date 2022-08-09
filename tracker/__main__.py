import tkinter as tk
from pathlib import Path

import cv2
import mss
import numpy

script_path = Path(__file__).parent
temp_dir = (script_path / '../data/template').resolve()
ui_files = [t for t in (temp_dir / 'ui').iterdir() if t.is_file() and t.name.endswith("png")]
ui_templates = list(map(lambda f: (f.name, cv2.imread(f.as_posix(), flags=cv2.IMREAD_GRAYSCALE)), ui_files))
headwear_files = [t for t in (temp_dir / 'headwear').iterdir() if t.is_file() and t.name.endswith("png")]
headwear_templates = list(map(lambda f: (f.name, cv2.imread(f.as_posix(), flags=cv2.IMREAD_GRAYSCALE)), headwear_files))


def screen_capture() -> numpy.ndarray:
    with mss.mss() as sct:
        monitor = {"top": 0, "left": 0, "width": 3440, "height": 1440}
        capture = numpy.array(sct.grab(monitor), dtype="uint8")
        return cv2.cvtColor(capture, cv2.COLOR_RGB2GRAY)


if __name__ == "__main__":
    window = tk.Tk()
    canvas = tk.Canvas(window, bg="white", width=3440, height=1400)
    label = tk.Label(window, bg="white")

    window.wm_attributes("-topmost", True)
    window.wm_attributes("-fullscreen", True)
    window.wm_attributes("-disabled", True)
    window.wm_attributes("-transparentcolor", "white")
    window.config(bg="white")

    while "Capturing Screen":
        screen = screen_capture()
        canvas.delete('all')
        detected_objects = []

        for name, template in headwear_templates:
            w, h, *d = template.shape[::-1]
            res = cv2.matchTemplate(screen, template, eval('cv2.TM_CCOEFF'))
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            if max_val > 2_000_000:
                detected_objects.append((name, top_left, bottom_right))

        for o in detected_objects:
            top_left = o[1]
            bottom_right = o[2]
            canvas.create_text(top_left[0], top_left[1] - 16, text=o[0], fill="red", font='Helvetica 12 bold')
            # canvas.create_rectangle(top_left[0], top_left[1], bottom_right[0], bottom_right[1], fill='red')

        canvas.pack(fill=tk.BOTH)
        window.update()
