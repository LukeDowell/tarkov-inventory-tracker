import unittest
from pathlib import Path

import cv2
import numpy

from matching import find_equipment_for_slot

script_path = Path(__file__).parent


class TestMatching(unittest.TestCase):
    def test_helmet_matching(self):
        helmet_files = (script_path / 'headwear_images').iterdir()

        def is_false_match(name: str, i: numpy.array) -> bool:
            e = find_equipment_for_slot('HEADWEAR', i)
            return e is None or e.name != name

        helmet_templates = map(
            lambda f: (f.name.replace('.png', ''), cv2.imread(f.as_posix(), cv2.IMREAD_GRAYSCALE)),
            helmet_files)

        false_matches = [t for t in helmet_templates if is_false_match(t[0], t[1])]

        assert len(false_matches) == 0
