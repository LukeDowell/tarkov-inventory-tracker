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
    ui_templates = list(
        map(lambda f: (f.name.replace('.png', ''), cv2.imread(f.as_posix(), flags=cv2.IMREAD_GRAYSCALE)), ui_files))
    equipment_templates: dict[str, dict] = {}

    for ui_name, _ in ui_templates:
        equipment_files = [t for t in (temp_dir / ui_name).iterdir() if t.is_file() and t.name.endswith("png")]
        templates_list = list(
            map(lambda f: (f.name.replace('.png', ''), cv2.imread(f.as_posix(), flags=cv2.IMREAD_GRAYSCALE)),
                equipment_files))
        equipment_templates[ui_name] = dict((name, temp) for name, temp in templates_list)

    while "Capturing Screen":
        screen = screen_capture()
        canvas.delete('all')
        debug_text = []
        debug_rect = []
        detected_slots = {}

        for name, template in ui_templates:
            slot_scan_size = (250, 50)
            min_val, max_val, min_loc, max_loc = template_match(screen, template)
            top_left = max_loc
            bottom_right = (top_left[0] + slot_scan_size[0], top_left[1] + slot_scan_size[1])
            if max_val > 5_500_000:
                # debug_text.append((name, top_left[0] - 15, top_left[1] - 20))
                detected_slots[name] = (top_left, bottom_right)

        for slot, (tl, br) in detected_slots.items():
            # debug_rect.append((tl, br))
            slot_cropped_img = screen[tl[1]:br[1], tl[0]:br[0]].copy()
            raw_matches = list(map(lambda et: (et[0], template_match(slot_cropped_img, et[1])), equipment_templates[slot].items()))
            raw_matches.sort(key=lambda m: m[1][1], reverse=True)
            maybe_match = next(iter(raw_matches), '')
            if not maybe_match == '':
                cv2.imshow('Template', equipment_templates[slot][maybe_match[0]])
                cv2.imshow('Src', slot_cropped_img)
                print(maybe_match)

        for d in debug_text:
            t, x, y = d
            canvas.create_text(x, y, text=t, fill="red", font='Helvetica 12 bold')

        for d in debug_rect:
            tl, br = d
            canvas.create_rectangle(tl[0], tl[1], br[0], br[1], outline='yellow', width=1)

        canvas.pack(fill=tk.BOTH)
        window.update()
