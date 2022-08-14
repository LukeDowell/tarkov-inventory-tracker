import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont

from equipment import ALL_SLOTS, Slot

script_path = Path(__file__).parent
item_json_path = (script_path / '../data/items.json').resolve()
font_bold_path = (script_path / '../data/Jovanny Lemonad - Bender-Bold.otf').resolve()
font_black_path = (script_path / '../data/Jovanny Lemonad - Bender-Black.otf').resolve()
temp_dir = (script_path / '../data/template').resolve()

item_size = 17
item_font = ImageFont.truetype(font_black_path.as_posix(), item_size)
ui_size = 20
ui_font = ImageFont.truetype(font_bold_path.as_posix(), 20)


@dataclass
class SlotTemplate:
    template: numpy.array
    item_templates: list[(str, numpy.array)]


def to_item_template(n: str, s: Slot = None, bg: (int, int, int) = (0, 0, 0), max_width: int = 165, **kwargs) -> Image:
    text_length = int(item_font.getlength(n)) + 2
    temp_img = ITEM_SLOT_BG.get(s, Image.new('RGB', (max_width, item_size), bg)).copy()
    img_width = temp_img.width
    pos = img_width - text_length - 1, 0
    if len(kwargs) == 0:
        ImageDraw.Draw(temp_img).text(pos, n, fill=(255, 255, 255), font=item_font,
                                      stroke_width=1, stroke_fill=(35, 35, 30))
    else:
        ImageDraw.Draw(temp_img).text(pos, n, **kwargs)

    if max_width < img_width:
        img = temp_img.crop((img_width - max_width, 0, img_width, temp_img.height))
    else:
        img = temp_img

    temp = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2GRAY)
    return temp


def to_ui_template(n: str) -> numpy.array:
    temp_w = int(ui_font.getlength(n)) + 2
    temp_img = Image.new('RGB', (temp_w, ui_size), (40, 40, 40))
    ImageDraw.Draw(temp_img).text((1, -1), n, fill=(211, 220, 220), font=ui_font, stroke_fill=(0, 0, 0))
    temp = cv2.cvtColor(numpy.array(temp_img), cv2.COLOR_RGB2GRAY)
    return temp


def slot_to_item_templates(n: Slot, **kwargs) -> list[(str, numpy.array)]:
    equipment_files = [t for t in (temp_dir / n).iterdir() if t.is_file() and t.name.endswith("png")]
    return list(map(
        lambda f: (f.name.replace('.png', ''), to_item_template(f.name.replace('.png', ''), n, **kwargs)),
        equipment_files))


ITEM_SLOT_BG: dict[Slot, numpy.array] = {
    'HEADWEAR': Image.open((temp_dir / 'UI/BG' / 'HEADWEAR.png').as_posix())
}

SLOT_TEMPLATES: dict[Slot, SlotTemplate] = dict(
    (s, SlotTemplate(t, i)) for s, t, i in map(lambda s: (s, to_ui_template(s), slot_to_item_templates(s)), ALL_SLOTS))


if __name__ == '__main__':
    ui_dir = (script_path / '../data/template/UI')
    if not ui_dir.exists() or not ui_dir.is_dir():
        ui_dir.mkdir()

    with open(item_json_path) as item_json_file:
        data = json.load(item_json_file)
        slots = list(data.keys())

        for slot in slots:
            slot_dir = (script_path / '../data/template' / slot)
            ui_temp = to_ui_template(slot)
            if not slot_dir.exists() or not slot_dir.is_dir():
                slot_dir.mkdir()
            # ui_temp.save((ui_dir / slot).resolve().as_posix() + '.png')

            for item in data[slot]:
                item_temp = to_item_template(item, slot)
                cv2.imwrite((slot_dir / item).as_posix() + '.png', item_temp)
