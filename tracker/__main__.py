from equipment import screen_capture, find_equipment_in_image
from pathlib import Path
import tkinter as tk
import cv2

script_path = Path(__file__).parent
headwear_dir = (script_path / '../data/template/headwear/processed').resolve()
headwear_files = [t for t in headwear_dir.iterdir() if t.is_file() and t.name.endswith("png")]
headwear_templates = list(map(lambda f: (f.name, cv2.imread(f.as_posix(), flags=cv2.IMREAD_ANYDEPTH)), headwear_files))

if __name__ == "__main__":
    window = tk.Tk()
    canvas = tk.Canvas(window, bg="white", width=3440, height=1400)
    label = tk.Label(window, bg="white")

    # window.overrideredirect(True)
    window.wm_attributes("-topmost", True)
    window.wm_attributes("-fullscreen", True)
    window.wm_attributes("-disabled", True)
    window.wm_attributes("-transparentcolor", "white")
    window.config(bg="white")

    while "Capturing Screen":
        print('tick')
        screen = screen_capture()
        canvas.delete('all')
        detected_objects = []

        for name, template in headwear_templates:
            w, h, *d = template.shape[::-1]
            res = cv2.matchTemplate(screen, template, eval('cv2.TM_CCOEFF'))
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            top_left = max_loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            print("Max - {max}\nMin - {min}".format(max=max_val, min=min_val))
            if max_val > 2_000_000:
                print('Adding {name}'.format(name=name))
                detected_objects.append((name, top_left, bottom_right))

        for o in detected_objects:
            print('Found {name}'.format(name=o[0]))
            top_left = o[1]
            bottom_right = o[2]
            canvas.create_text(top_left[0], top_left[1] - 16, text=o[0], fill="red", font='Helvetica 12 bold')
            # canvas.create_rectangle(top_left[0], top_left[1], bottom_right[0], bottom_right[1], fill='red')

        canvas.pack(fill=tk.BOTH)
        window.update()
