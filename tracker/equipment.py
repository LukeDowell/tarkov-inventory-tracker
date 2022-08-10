from typing import Literal, Set

Slot = Literal['ARMBAND', 'BACKPACK', 'BODY ARMOR', 'EARPIECE', 'EYEWEAR', 'FACE COVER', 'HEADWEAR', 'HOLSTER',
               'ON BACK', 'ON SLING', 'SHEATH', 'TACTICAL RIG']

ALL_SLOTS: Set[Slot] = {'ARMBAND', 'BACKPACK', 'BODY ARMOR', 'EARPIECE', 'EYEWEAR', 'FACE COVER', 'HEADWEAR', 'HOLSTER',
                        'ON BACK', 'ON SLING', 'SHEATH', 'TACTICAL RIG'}
