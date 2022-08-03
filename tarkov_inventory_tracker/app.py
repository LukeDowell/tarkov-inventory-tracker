from tkinter import Image

from matplotlib import pyplot as plt
from matplotlib import image as mpimg
import cv2
import mss
import numpy


# with mss.mss() as sct:
#     # Part of the screen to capture
#     monitor = {"top": 0, "left": 0, "width": 1000, "height": 1000}
#
#     while "Screen capturing":
#         last_time = time.time()
#
#         # Get raw pixels from the screen, save it to a Numpy array
#         img = numpy.array(sct.grab(monitor))
#
#         # Display the picture
#         cv2.imshow("OpenCV/Numpy normal", img)
#
#         # Display the picture in grayscale
#         # cv2.imshow('OpenCV/Numpy grayscale',
#         #            cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY))
#
#         print("fps: {}".format(1 / (time.time() - last_time)))
#
#         # Press "q" to quit
#         if cv2.waitKey(25) & 0xFF == ord("q"):
#             cv2.destroyAllWindows()
#             break

img = cv2.imread('../tests/res/stash-screenshot-gear.png', 0)
img2 = img.copy()
template = cv2.imread('../data/template/ui/headwear.png', 0)
w, h = template.shape[::-1]

methods = ['cv2.TM_CCOEFF', 'cv2.TM_CCOEFF_NORMED', 'cv2.TM_CCORR',
           'cv2.TM_CCORR_NORMED', 'cv2.TM_SQDIFF', 'cv2.TM_SQDIFF_NORMED']

for meth in methods:
    img = img2.copy()
    method = eval(meth)
    # Apply template Matching
    res = cv2.matchTemplate(img, template, method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
    if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
        top_left = min_loc
    else:
        top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    cv2.rectangle(img, top_left, bottom_right, (255, 255, 255), 4)
    plt.figure(figsize=(20, 10), dpi=100)
    plt.imshow(img)
    plt.title('Detected Point'), plt.xticks([]), plt.yticks([])
    plt.suptitle(meth)
    plt.show()
