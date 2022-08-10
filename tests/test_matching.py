import unittest
from pathlib import Path

import cv2

from matching import get_slot_image, find_equipment_for_slot

script_path = Path(__file__).parent


class TestMatching(unittest.TestCase):
    def test_item_matching(self):
        test_scr_img = cv2.imread((script_path / 'stash-screenshot-gear.png').as_posix(), cv2.IMREAD_GRAYSCALE)
        slot_img = get_slot_image('HEADWEAR', test_scr_img)
        equipment = find_equipment_for_slot('HEADWEAR', slot_img)
        assert equipment is not None
        assert equipment.name == '6B47'
