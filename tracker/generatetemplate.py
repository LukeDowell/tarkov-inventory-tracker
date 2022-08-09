from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def to_item_template(n: str, font: ImageFont) -> (str, Image):
    temp_w = int(font.getlength(n)) + 2
    temp_img = Image.new('RGBA', (temp_w, 17), (0, 0, 0, 0))
    ImageDraw.Draw(temp_img).text((1, -1), n, fill=(211, 220, 220), font=font, stroke_width=1, stroke_fill=(0, 0, 0))
    return n, temp_img


def to_ui_template(n: str, font: ImageFont) -> (str, Image):
    temp_w = int(font.getlength(n)) + 2
    temp_img = Image.new('RGB', (temp_w, 20), (40, 40, 40))
    ImageDraw.Draw(temp_img).text((1, -1), n, fill=(211, 220, 220), font=font, stroke_fill=(0, 0, 0))
    return n, temp_img


if __name__ == '__main__':
    script_path = Path(__file__).parent
    font_bold_path = (script_path / '../data/Jovanny Lemonad - Bender-Bold.otf').resolve()

    ui_templates_to_build = [
        "HEADWEAR",
        "EARPIECE",
        "EYEWEAR",
        "ON SLING",
        "ON BACK",
        "ARMBAND",
        "SHEATH",
        "HOLSTER",
        "FACE COVER",
        "TACTICAL RIG",
        "BACKPACK"
    ]

    ui_font = ImageFont.truetype(font_bold_path.as_posix(), 20)
    for name, image in map(lambda n: to_ui_template(n, ui_font), ui_templates_to_build):
        image.save((script_path / '../data/template/ui' / name).resolve().as_posix() + '.png')

    headwear_templates_to_build = [
        '6B47',
        'TC-2001',
        'TC-2002',
        'UNTAR',
        'Tactical Sport',
        'Momex',
        'Condor',
        'AK-105',
        'Day Pack',
    ]

    item_font = ImageFont.truetype(font_bold_path.as_posix(), 17)
    for name, image in map(lambda n: to_item_template(n, item_font), headwear_templates_to_build):
        image.save((script_path / '../data/template/headwear' / name).resolve().as_posix() + '.png')
