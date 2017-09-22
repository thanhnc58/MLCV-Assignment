import math
from collections import deque

import cv2
import numpy as np

queue = deque([])

MHI_DURATION = 40  # 0.7  # 0.5
DEFAULT_THRESHOLD = 250  # 32
MAX_TIME_DELTA = 40  # 0.25  # 0.25
MIN_TIME_DELTA = 1  # 0.05
# motion_history = np.zeros((h, w), np.float32)
motion_history = np.zeros((1, 1), np.float32)
prv_foreground = np.zeros((1, 1), np.float32)
prv_area = 0


def draw_motion_comp(vis, rect, angle, color):
    # return
    x, y, w, h = rect
    cv2.rectangle(vis, (x, y), (x + int(w), y + int(h)), (0, 255, 0))
    r = math.floor(min(w / 2, h / 2))
    cx, cy = math.floor(x + w / 2), math.floor(y + h / 2)
    angle = angle * np.pi / 180
    # cv2.circle(vis, (cx, cy), r, color, 3)
    cv2.line(vis, (int(cx), int(cy)), (int(cx + np.cos(angle) * r), int(cy + np.sin(angle) * r)), color, 3)


def update(foreground, frame_index, orient_type=1):
    global motion_history
    global prv_area
    global prv_foreground

    h, w = foreground.shape[:2]
    ph, pw = motion_history.shape[:2]
    foreground_area = cv2.countNonZero(foreground)

    # Remove noise
    dn = False
    if 0 < foreground_area < prv_area:
        if math.fabs(foreground_area - prv_area) > (0.4 * prv_area):
            dn = True

    # Set previous foreground and fg area
    prv_area = foreground_area
    prv_foreground = foreground.copy()
    
    # Compare frame
    if ph != h or pw != w or foreground_area < 100 or dn or frame_index == 0:
        motion_history = np.zeros((h, w), np.float32)
        prv_foreground = np.zeros((h, w), np.float32)

    # Calculate MHI
    ret, motion_mask = cv2.threshold(foreground, 254, 1, cv2.THRESH_BINARY)
    
    timestamp = frame_index + 10  # common.clock()

    cv2.motempl.updateMotionHistory(motion_mask, motion_history, timestamp, MHI_DURATION)

    mg_mask, mg_orient = cv2.motempl.calcMotionGradient(motion_history, MAX_TIME_DELTA, MIN_TIME_DELTA,
                                                        apertureSize=7)
    seg_mask, seg_bounds = cv2.motempl.segmentMotion(motion_history, timestamp, MAX_TIME_DELTA)

    vis = np.uint8(np.clip((motion_history - (timestamp - MHI_DURATION)) / MHI_DURATION, 0, 1) * 255)

    # cv2.imshow("MHI",vis)

    m_rect = (0, 0, 0, 0)
    for i, rect in enumerate([(0, 0, w, h)] + list(seg_bounds)):
        x, y, rw, rh = rect
        if (x != 0) and (y != 0):
            area = rw * rh
            m_area = m_rect[2] * m_rect[3]
            if area > m_area:
                m_rect = rect

    x, y, rw, rh = m_rect

    color = ((255, 0, 0), (0, 0, 255))[i == 0]
    vis_2 = cv2.cvtColor(vis, cv2.COLOR_GRAY2BGR)
    

    angle = 0
    if orient_type == 0: # common method
        # silh_roi = motion_mask[y:y + rh, x:x + rw]
        print "asdfadsfafsd"
        orient_roi = mg_orient[y:y + rh, x:x + rw]
        mask_roi = mg_mask[y:y + rh, x:x + rw]
        mhi_roi = motion_history[y:y + rh, x:x + rw]
        angle = cv2.motempl.calcGlobalOrientation(orient_roi, mask_roi, mhi_roi, timestamp, MHI_DURATION)
        draw_motion_comp(vis_2, m_rect, angle, color)
    # else:

    # Calculate motion magnitude and motion orientation
    ret, recent = cv2.threshold(vis, 100, 255, cv2.THRESH_BINARY)
    image, contours, hierarchy = cv2.findContours(recent, 1, 2)
    magnitude = 0
    mass_speed = 0
    if len(contours) > 0:
        max_cnt = contours[0]
        for cnt in contours:
            a = cv2.contourArea(cnt)
            if a > cv2.contourArea(max_cnt):
                max_cnt = cnt
        m = cv2.moments(max_cnt)
        centroid_x = int(m['m10'] / m['m00'])
        centroid_y = int(m['m01'] / m['m00'])
        mc = (centroid_x, centroid_y)
        cv2.circle(vis_2, mc, 2, (0, 255, 255), 3)



        if len(queue) > 0:
            prv = queue[len(queue) - 1]
            distance = math.sqrt(math.pow(mc[0] - prv[0], 2) + math.pow(mc[1] - prv[1], 2))
            if distance >= 22:
                for i in range(1, len(queue) + 1):
                    queue[i - 1] = mc

        queue.append(mc)
        if len(queue) == 15:
            queue.popleft()
            
            mass_speed = math.sqrt(math.pow(mc[0] - queue[0][0], 2) + math.pow(mc[1] - queue[0][1], 2))
            # print ("%d,%d  / %d,%d / %d" %(mc[0],mc[1],queue[0][0], queue[0][1], mass_speed))

        _, cur_contours, _ = cv2.findContours(foreground, 1, 2)
        if len(cur_contours) > 0:
            cur_M = cv2.moments(cur_contours[0])
            cur_centroid_x = int(cur_M['m10'] / cur_M['m00'])
            cur_centroid_y = int(cur_M['m01'] / cur_M['m00'])
            cur_MC = (cur_centroid_x, cur_centroid_y)
            cv2.circle(vis_2, cur_MC, 2, (255, 255, 0), 3)
            # cv2.imshow("Center_of_mass",vis_2)

            dx = cur_centroid_x - centroid_x
            dy = cur_centroid_y - centroid_y

            magnitude = math.sqrt(dx * dx + dy * dy)

            if dx != 0 and orient_type == 1: # proposed method

                angle = math.atan(math.fabs(dy) / math.fabs(dx))
                if dx > 0 and dy > 0:
                    angle = angle
                elif dx > 0 > dy:
                    angle = (2 * math.pi) - angle
                elif dx < 0 and dy < 0:
                    angle = angle + math.pi
                elif dx < 0 < dy:
                    angle = math.pi - angle


                angle *= (180 / math.pi)
                # print ("dx %f , %f , %f " %(dx, dy , dx/dy))
                draw_motion_comp(vis_2, m_rect, angle, color)
                # else:
                #     angle = -1

    cur_m = cv2.countNonZero(motion_mask)
    # print cur_m
    all_m = cv2.countNonZero(vis)
    pass_m = all_m - cur_m
    if all_m > 0 and cur_m > 400:
        motion_ratio = round(100 * (pass_m / all_m), 0)
    else:
        motion_ratio = 0
        # motion_ratio = motion_ratio * magnitude
    # motion_ratio = magnitude  
    return vis, vis_2, angle, magnitude, motion_ratio, mass_speed
