import math
from collections import deque

queue = deque([])
large_motion_frame = -1
move_down_frame = -1
apparently_fall_frame = -1

CONST_MC_SPEED_1 = 0  # Lecture: 15; Coffee_room: 18;    Office: 18
CONST_MRATE_1 = 65  # Lecture: 60; Coffee_room: 60;    Office: 65
CONST_MAGN_1 = 30  # Lecture: 12; Coffee_room: 23;            30

CONST_MC_SPEED_2 = 79  # Lecture: 20; Coffee_room: 25;            25
CONST_MRATE_2 = 50  # Lecture: 40; Coffee_room: 40;            50
CONST_MAGN_2 = 20  # Lecture: 10; Coffee_room: 15;            20

CONST_AR = .5
CONST_ANGLE = 0  # 0 - 20

MIN_CONT_AREA = 40 ** 2  # 40 - 70
MAX_CONT_AREA = 150 ** 2


def predict(motion_angle, motion_magnitude,
            foreground_area, frame_index):
    result = 0
    global large_motion_frame
    global move_down_frame
    global apparently_fall_frame
    if frame_index == 0:
        large_motion_frame = -1
        move_down_frame = -1
        apparently_fall_frame = -1
    print '  ' + str(foreground_area)

    # if it can be fall, observe in 20 following frame if it dont have any movement then give a conclusion 
    if apparently_fall_frame > 0:
        if (frame_index - apparently_fall_frame) > 50:
            large_motion_frame = -1
            move_down_frame = -1
            apparently_fall_frame = -1
            if foreground_area < 0.5 * MIN_CONT_AREA: #foreground_extractor.MIN_CONT_AREA:
                return 2
            else:
                return 0                   
        else:
            result = 1

    # mark frame has fast movement

    if (MIN_CONT_AREA < foreground_area < MAX_CONT_AREA) and (((
                    60 > motion_magnitude >= CONST_MAGN_1) ) or ( (
                            60 > motion_magnitude > CONST_MAGN_2))) and (0 <= motion_angle <= 180):
        large_motion_frame = frame_index

    # if it has fast movement, observe direction of movement in 20 following frame
    # out of 20 frame suppose to be not fall, observe again
    if large_motion_frame > 0:
        if frame_index - large_motion_frame <= 30:
            if (MIN_CONT_AREA < foreground_area < MAX_CONT_AREA) and (35 <= motion_angle <= 140):  # 40 - 140
                move_down_frame = frame_index
        else:
            large_motion_frame = -1
            move_down_frame = -1

    if move_down_frame > 0:
        apparently_fall_frame = frame_index
    
    return result
