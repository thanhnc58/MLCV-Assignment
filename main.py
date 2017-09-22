#!/usr/bin/env python
import sys

sys.path.insert(0, "/home/thanh/Desktop/final")
# sys.path.insert(0, "E:/Sources/ComputerVision/EventDetection/FallDetection/final")
import cv2
import time

cv2.ocl.setUseOpenCL(False)

import common
import input
import foreground_extractor
import mhi
import shape
import detect2
# import alarm

SHOW_MHI = 1
SHOW_FOREGROUND = 0
SHOW_COEFFICIENT = 1
SHOW_VIDEO_INFOR = 1

if __name__ == '__main__':
    fall_frame = -1
    input.init(2, 1)
    slow_motion = False
    while 1:
        e1 = cv2.getTickCount()

        # 1. Read video from camera
        frame, index, video_name = input.get_next_frame()
        if frame is None:
            break
        
        # 2. Get foreground using mixture of gaussian
        foreground, area = foreground_extractor.mog2(frame, index, True)
        if SHOW_FOREGROUND: cv2.imshow("foreground", foreground)

        # 3. Caculate motion magnitude and motion orientation
        vis, vis_orient, angle, magnitude, motion_ratio, m_speed = mhi.update(foreground, index, 1)
        if SHOW_MHI:  cv2.imshow("Motion_orientation", vis_orient)

        # Show motion orientation
        _, sh = cv2.threshold(vis, 250, 255, cv2.THRESH_BINARY)
        sh = foreground
        cv2.imshow("sh", sh)
        

        e2 = cv2.getTickCount()
        time = (e2 - e1) / cv2.getTickFrequency()

        # 4. Predict Fall
        fall = detect2.predict(angle, magnitude, area, index)

        # Show imformation
        if SHOW_COEFFICIENT:
            common.draw_str(frame, (5, 10), "MO: " + str(round(angle, 2)))
            common.draw_str(frame, (5, 85), "SP: " + str(round(motion_ratio, 2)))
            common.draw_str(frame, (5, 100), "MAG: " + str(round(magnitude, 2)))

        if SHOW_VIDEO_INFOR:
            common.draw_str(frame, (210, 15), "FR: " + str(index))
            common.draw_str(frame, (210, 30), "VD: " + str(video_name))
            common.draw_str(frame, (210, 210), "spd(f/s):    " + str(round(1 / time, 1)))
        print ('%d mag %d ang %d' %(index,magnitude,angle,)) 
        
        # Show Alert
        if fall == 2:
            if fall_frame < 0:
                fall_frame = index
                print "asdfasdffads"
                # alarm.start_alarm()
        elif fall == 1:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, 'OO', (100, 100), font, 1, (0, 255, 255), 2, cv2.LINE_AA)

        if index > 0 and fall_frame > 0 and index - fall_frame < 100:
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(frame, 'OOPS!', (100, 100), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
        else:
            fall_frame = -1

        if slow_motion:
            cv2.imshow("frame", frame)
            k = cv2.waitKey() & 0xff
            if k == 112:
                slow_motion = False
        else:
            k = cv2.waitKey(1) & 0xff

        e2 = cv2.getTickCount()
        time = (e2 - e1) / cv2.getTickFrequency()
        
        # common.draw_str(frame, (210, 230), "f-rate(f/s): " + str(round(1 / time, 1)))

        if k == 112:
            cv2.imshow("frame", frame)
            k = cv2.waitKey() & 0xff
            if k == 110:
                slow_motion = True
        elif k == 110:
            slow_motion = True
        elif k == 27:
            break
    
        cv2.imshow("Human_shape", frame)

    input.release()

    cv2.destroyAllWindows()
