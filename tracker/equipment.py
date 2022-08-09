import cv2


def find_equipment_in_image(img, template) -> (int, int, int):
    """
    Parses equipment out of an image
    :param img:
    :param template:
    :return:
    """
    w, h = template.shape[::-1]
    res = cv2.matchTemplate(img, template, eval('cv2.TM_CCOEFF'))
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    return max_val, top_left, bottom_right
