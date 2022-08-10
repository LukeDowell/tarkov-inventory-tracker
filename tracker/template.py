import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy
from PIL import Image, ImageDraw, ImageFont

from equipment import ALL_SLOTS, Slot

script_path = Path(__file__).parent
temp_dir = (script_path / '../data/template').resolve()
font_normal_path = (script_path / '../data/Jovanny Lemonad - Bender-Bold.otf').resolve()
font_bold_path = (script_path / '../data/Jovanny Lemonad - Bender-Bold.otf').resolve()
item_json_path = (script_path / '../data/items.json').resolve()


def slot_to_item_templates(n: Slot) -> list[(str, numpy.array)]:
    equipment_files = [t for t in (temp_dir / n).iterdir() if t.is_file() and t.name.endswith("png")]
    # return list(map(lambda f: (f.name.replace('.png', ''), cv2.imread(f.as_posix(), flags=cv2.IMREAD_GRAYSCALE)),
    #                 equipment_files))
    return list(
        map(lambda f: (f.name.replace('.png', ''), to_item_template(f.name.replace('.png', ''))), equipment_files))


item_size = 17
item_font = ImageFont.truetype(font_bold_path.as_posix(), item_size)
ui_size = 20
ui_font = ImageFont.truetype(font_bold_path.as_posix(), 20)


def to_item_template(n: str, *args) -> Image:
    temp_w = int(item_font.getlength(n)) + 2
    temp_img = Image.new('RGB', (temp_w, item_size), (0, 0, 0))
    if len(args) == 0:
        ImageDraw.Draw(temp_img).text((1, -1), n, fill=(211, 220, 220), font=item_font, stroke_width=1,
                                      stroke_fill=(35, 35, 30))
    else:
        ImageDraw.Draw(temp_img).text((1, -1), n, font=item_font, *args)
    return cv2.cvtColor(numpy.array(temp_img), cv2.COLOR_RGB2GRAY)


def to_ui_template(n: str) -> numpy.array:
    temp_w = int(ui_font.getlength(n)) + 2
    temp_img = Image.new('RGB', (temp_w, ui_size), (40, 40, 40))
    ImageDraw.Draw(temp_img).text((1, -1), n, fill=(211, 220, 220), font=ui_font, stroke_fill=(0, 0, 0))
    return cv2.cvtColor(numpy.array(temp_img), cv2.COLOR_RGB2GRAY)


@dataclass
class SlotTemplate:
    template: numpy.array
    item_templates: list[(str, numpy.array)]


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
            ui_temp.save((ui_dir / slot).resolve().as_posix() + '.png')

            for item in data[slot]:
                item_temp = to_item_template(item)
                item_temp.save((slot_dir / item).resolve().as_posix() + '.png')
