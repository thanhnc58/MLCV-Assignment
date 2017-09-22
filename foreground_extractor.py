import numpy as np
import cv2

cv2.ocl.setUseOpenCL(False)

MIN_CONT_AREA = 40 ** 2  # 40 why
MAX_CONT_AREA = 150 ** 2 # why 

priv_mc = (0, 0)

fgbg_mog2 = cv2.createBackgroundSubtractorMOG2(300, 40, True) # why 300, 40
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))


def reset():
    global fgbg_mog2
    global kernel
    fgbg_mog2 = cv2.createBackgroundSubtractorMOG2(300, 40, True)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))


def mog2_pos(img):
    fgmask = fgbg_mog2.apply(img)
    kernel1 = np.ones((3, 3), np.uint8)
    erosion = cv2.erode(fgmask, kernel1, iterations=1)
    fgmask = cv2.dilate(erosion, kernel1, iterations=7)
    return fgmask


def mog2(img, frame_index, post_proc=True):
    if frame_index == 0:
        reset()

    # Background subtraction
    fgmask = fgbg_mog2.apply(img)

    # Remove shadow
    _, fgmask = cv2.threshold(fgmask, 127, 255, cv2.THRESH_BINARY)
    

    # Remove noise
    if post_proc:
        kernel1 = np.ones((3, 3), np.uint8)
        erosion = cv2.erode(fgmask, kernel1, iterations=1)

        kernel1 = np.ones((5, 5), np.uint8)
        fgmask = cv2.dilate(erosion, kernel1, iterations=3) #why not use MORPH_OPEN



        kernel = np.ones((7, 7), np.uint8)
        fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_CLOSE, kernel)


    cv2.imshow("foregrounddddddddd",fgmask)
    # Find contours
    image, contours, hierarchy = cv2.findContours(fgmask, 1, 2)


    maxCnt_img = fgmask.copy()
    maxCnt_img[:] = 0
    c_area = 0
    global priv_mc

    # Find a max contour in image
    # print len(contours)
    if len(contours) > 0:
        max_nct = contours[0]
        for cnt in contours:
            a = cv2.contourArea(cnt)
            if cv2.contourArea(max_nct) < a:  # <= MAX_CONT_AREA:
                max_nct = cnt
        rect = cv2.minAreaRect(max_nct)
        (x, y), (w, h), rect_angle = rect
        c_area = w * h
        
        if MIN_CONT_AREA < c_area < MAX_CONT_AREA :
            cv2.drawContours(maxCnt_img, [max_nct], 0, (255, 255, 255), -1)
            cv2.imshow("afsdfadsafds", maxCnt_img)
            # print c_area
    return maxCnt_img, c_area
