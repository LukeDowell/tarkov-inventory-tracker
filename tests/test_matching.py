import time
import unittest
from pathlib import Path

import cv2
import numpy
import numpy as np
from PIL import ImageFont

from matching import find_equipment_for_slot, template_match
from template import slot_to_item_templates, SLOT_TEMPLATES

script_path = Path(__file__).parent


class TestMatching(unittest.TestCase):

    def test_helmet_matching(self):
        def is_false_match(name: str, i: numpy.array) -> bool:
            e = find_equipment_for_slot('HEADWEAR', i)
            return e is None or e.name != name

        headwear_files = (script_path / 'headwear_images').iterdir()
        helmet_templates = map(lambda f: (f.name.replace('.png', ''), cv2.imread(f.as_posix(), cv2.IMREAD_UNCHANGED)),
                               headwear_files)
        false_matches = [t for t in helmet_templates if is_false_match(t[0], t[1])]
        assert len(false_matches) == 0

    def test_best_settings(self):
        headwear_files = (script_path / 'headwear_images').iterdir()

        font_sizes = [16, 17, 18]
        font_files = ['Bender-Black', 'Bender-Bold',
                      'Bender-Light', 'Bender'
                      ]
        background_colors = [
            (0, 0, 0),
            (255, 255, 255),
        ]
        stroke_widths = [1]
        stroke_fills = [
            (35, 35, 30),
            (0, 0, 0),
            (100, 100, 100),
        ]
        text_fills = [
            (255, 255, 255),
            (211, 220, 220)
        ]
        masks = [True, False]
        results = []

        Color = (int, int, int)

        headwear_slot_templates = list(map(
            lambda f: (f.name.replace('.png', ''), cv2.imread(f.as_posix(), cv2.IMREAD_GRAYSCALE)),
            headwear_files))

        def get_results(fs: int, ff: str, bg: Color, sw: int, sf: Color, tf: Color, m: bool):
            font_path = script_path / '../data/Jovanny Lemonad - {f}.otf'.format(f=ff)
            font = ImageFont.truetype(font_path.as_posix(), fs)
            slot_templates = slot_to_item_templates('HEADWEAR', font=font, fill=tf, bg=bg, stroke_width=sw,
                                                    stroke_fill=sf)

            rl = []
            for expected, test_img in headwear_slot_templates:
                equipment = find_equipment_for_slot('HEADWEAR',
                                                    test_img,
                                                    slot_templates,
                                                    lambda s, t: template_match(s, t)
                                                    )
                # r.append((expected, equipment, fs, ff, bg, sw, sf, tf, m))
                r = (expected, equipment.name, equipment.result[1], fs, ff, bg, sw, sf, tf, m)
                rl.append(r)

            return rl

        start = time.time()
        for fs in font_sizes:
            for ff in font_files:
                for bg in background_colors:
                    for sw in stroke_widths:
                        for sf in stroke_fills:
                            for tf in text_fills:
                                for m in masks:
                                    results.append(get_results(fs, ff, bg, sw, sf, tf, m))

        print("Took {time} millis".format(time=time.time() - start))
        best_result = sorted(results, key=lambda res: len(list(filter(lambda r: r[0] == r[1], res))), reverse=True)[0]
        num_wrong = len(list(filter(lambda l: l[0] != l[1], best_result)))
        best = best_result[0]
        print("""
        Num Wrong: {nw} 
        Best settings for item matching:
            Font Size: {fs}
            Font: {ff}
            Background Color: {bg}
            Stroke Width: {sw}
            Stroke Fill: {sf}
            Text Fill: {tf}
            Mask: {m}
        """.format(nw={num_wrong}, fs=best[3], ff=best[4], bg=best[5], sw=best[6], sf=best[7], tf=best[8], m=best[9]))

    def test_edge_detection(self):
        headwear_files = (script_path / 'headwear_images').iterdir()
        headwear_subjects = list(map(
            lambda f: (f.name.replace('.png', ''), cv2.imread(f.as_posix(), cv2.IMREAD_GRAYSCALE)),
            headwear_files))

        [_, s] = headwear_subjects[1]
        blur = cv2.GaussianBlur(s, (3, 3), 0)
        sobelx = cv2.Sobel(src=blur, ddepth=cv2.CV_64F, dx=1, dy=0, ksize=1)
        sobely = cv2.Sobel(src=blur, ddepth=cv2.CV_64F, dx=0, dy=1, ksize=1)
        sobel = cv2.Sobel(src=blur, ddepth=cv2.CV_64F, dx=1, dy=1, ksize=1)
        edges = cv2.Canny(image=blur, threshold1=1, threshold2=1)

        def blur_temp(n: str, t: numpy.array) -> (str, numpy.array):
            t_blur = cv2.GaussianBlur(t, (3, 3), 0)
            t_edges = cv2.Canny(image=t_blur, threshold1=1, threshold2=1)
            return n, t_edges

        edge_templates: list[(str, numpy.array)] = list(
            map(lambda t: blur_temp(t[0], t[1]), SLOT_TEMPLATES['HEADWEAR'].item_templates))

        equipment = find_equipment_for_slot('HEADWEAR', s, SLOT_TEMPLATES['HEADWEAR'].item_templates)
