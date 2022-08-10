import json
import tkinter as tk
from pathlib import Path

import cv2
import mss
import numpy

from equipment import Slot
from matching import get_slot_image, find_equipment_for_slot, EquipmentMatch
from template import SLOT_TEMPLATES

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

    while "Capturing Screen":
        screen = screen_capture()
        canvas.delete('all')
        debug_text = []
        debug_rect = []
        detected_slots = {}

        slot_to_cropped_img = map(lambda s: (s, get_slot_image(s, screen)), SLOT_TEMPLATES.keys())
        slot_to_item_results = map(lambda s: (s[0], find_equipment_for_slot(s[0], s[1])), slot_to_cropped_img)
        slot_to_worn_item: dict[Slot, EquipmentMatch] = dict((n, r) for n, r in slot_to_item_results)

        headwear = slot_to_worn_item['HEADWEAR']
        print(
            'Wearing {item} with confidence of {conf} in HEADWEAR'.format(item=headwear.name, conf=headwear.result[1]))

        for d in debug_text:
            t, x, y = d
            canvas.create_text(x, y, text=t, fill="red", font='Helvetica 12 bold')

        for d in debug_rect:
            tl, br = d
            canvas.create_rectangle(tl[0], tl[1], br[0], br[1], outline='yellow', width=1)

        canvas.pack(fill=tk.BOTH)
        window.update()
