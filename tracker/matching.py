from dataclasses import dataclass
from typing import Optional

import cv2
import numpy

from equipment import Slot
from template import SLOT_TEMPLATES

MatchResult = (float, float, (int, int), (int, int))


@dataclass
class EquipmentMatch:
    name: str
    slot: Slot
    result: MatchResult


@dataclass
class SlotResult:
    slot: str
    slot_img: numpy.array
    equipment_found: list[EquipmentMatch]


def find_equipment_for_slot(slot: Slot,
                            src: numpy.array,
                            templates: list[str, numpy.array],
                            threshold: float = .80) -> Optional[EquipmentMatch]:
    item_results = list(map(lambda t: (t[0], template_match(src, t[1])), templates))
    item_results.sort(key=lambda t: t[1][1], reverse=True)
    if len(item_results) == 0:
        return None
    result: (str, MatchResult) = item_results[0]
    return EquipmentMatch(result[0], slot, result[1])


SLOT_SIZE_OVERRIDE: dict[Slot, (int, int)] = {}


def get_slot_image(slot: Slot, src: numpy.array, threshold: float = .80) -> Optional[numpy.array]:
    slot_size = SLOT_SIZE_OVERRIDE.get(slot, (170, 50))
    _, max_val, _, max_loc = template_match(src, SLOT_TEMPLATES[slot].template)
    tl = max_loc
    br = (tl[0] + slot_size[0], tl[1] + slot_size[1])
    return src[tl[1]:br[1], tl[0]:br[0]].copy()
    # if max_val > threshold:
    #     return src[tl[1]:br[1], tl[0]:br[0]].copy()
    # return None


def template_match(img: numpy.array, temp: numpy.array) -> MatchResult:
    mask = cv2.inRange(temp, numpy.array([1]), numpy.array([255]))
    res = cv2.matchTemplate(img, temp, cv2.TM_CCORR_NORMED, mask=mask)
    return cv2.minMaxLoc(res)
