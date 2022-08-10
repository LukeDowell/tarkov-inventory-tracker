from dataclasses import dataclass
from typing import Optional

import cv2
import numpy

from equipment import Equipment, Slot
from template import SLOT_TEMPLATES


@dataclass
class SlotResult:
    slot: str
    slot_img: numpy.array
    equipment_found: list[Equipment]


def find_equipment_for_slot(slot: Slot, src: numpy.array, threshold: int = 2_000_000) -> Optional[Equipment]:
    item_results = list(map(lambda t: (t[0], template_match(src, t[1])), SLOT_TEMPLATES[slot].item_templates))
    # likely_results = list(filter(lambda t: t[1][1] > threshold, item_results))
    item_results.sort(key=lambda t: t[1][1], reverse=True)
    if len(item_results) == 0:
        return None
    return Equipment(item_results[0][0], slot)


SLOT_SIZE_OVERRIDE: dict[Slot, (int, int)] = {}


def get_slot_image(slot: Slot, src: numpy.array, threshold: int = 5_500_000) -> Optional[numpy.array]:
    slot_size = SLOT_SIZE_OVERRIDE.get(slot, (170, 50))
    _, max_val, _, max_loc = template_match(src, SLOT_TEMPLATES[slot].template)
    tl = max_loc
    br = (tl[0] + slot_size[0], tl[1] + slot_size[1])
    if max_val > threshold:
        return src[tl[1]:br[1], tl[0]:br[0]].copy()
    return None


MatchResult = (int, int, (int, int), (int, int))


def template_match(img: numpy.array, temp: numpy.array) -> MatchResult:
    res = cv2.matchTemplate(img, temp, eval('cv2.TM_CCOEFF'))
    return cv2.minMaxLoc(res)
