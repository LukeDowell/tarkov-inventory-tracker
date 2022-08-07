from matplotlib import pyplot as plt
import mss
import numpy
import time
import cv2


template = cv2.imread('./data/template/ui/headwear.png', flags=cv2.IMREAD_GRAYSCALE)
w, h = template.shape[::-1]

with mss.mss() as sct:
    # Part of the screen to capture
    monitor = {"top": 0, "left": 0, "width": 3440, "height": 1440}
    while "Screen capturing":
        last_time = time.time()
        capture = numpy.array(sct.grab(monitor), dtype="uint8")
        capture_img = cv2.cvtColor(capture, cv2.COLOR_BGR2GRAY)

        methods = [
            'cv2.TM_CCOEFF',
            # 'cv2.TM_CCOEFF_NORMED',
            # 'cv2.TM_CCORR',
            # 'cv2.TM_CCORR_NORMED',
            # 'cv2.TM_SQDIFF',
            # 'cv2.TM_SQDIFF_NORMED'
        ]

        for meth in methods:
            img = capture_img.copy()
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

        # Press "q" to quit
        if cv2.waitKey(25) & 0xFF == ord("q"):
            cv2.destroyAllWindows()
            break
