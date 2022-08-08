from unittest import TestCase

from tracker.equipment import *


class TestEquipment(TestCase):
    def test_screen_capture(self):
        script_path = Path(__file__).parent
        tmp_path = (script_path / '../data/template/ui/headwear.png').resolve()
        template = cv2.imread(tmp_path.as_posix(), flags=cv2.IMREAD_GRAYSCALE)
        screen = screen_capture()
        coords = find_equipment_in_image(screen, template)
        assert coords[0] == 1 and coords[1] == 2
