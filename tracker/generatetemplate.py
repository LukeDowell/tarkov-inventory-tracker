import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

script_path = Path(__file__).parent
font_bold_path = (script_path / '../data/Jovanny Lemonad - Bender-Bold.otf').resolve()
item_json_path = (script_path / '../data/items.json').resolve()
item_font = ImageFont.truetype(font_bold_path.as_posix(), 17)
ui_font = ImageFont.truetype(font_bold_path.as_posix(), 20)


def to_item_template(n: str) -> Image:
    temp_w = int(item_font.getlength(n)) + 2
    temp_img = Image.new('RGBA', (temp_w, 17), (0, 0, 0, 0))
    ImageDraw.Draw(temp_img).text((1, -1), n, fill=(211, 220, 220), font=item_font, stroke_width=1,
                                  stroke_fill=(0, 0, 0))
    return temp_img


def to_ui_template(n: str) -> Image:
    temp_w = int(ui_font.getlength(n)) + 2
    temp_img = Image.new('RGB', (temp_w, 20), (40, 40, 40))
    ImageDraw.Draw(temp_img).text((1, -1), n, fill=(211, 220, 220), font=ui_font, stroke_fill=(0, 0, 0))
    return temp_img


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
