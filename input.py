import cv2
import os.path

dataset_url1 = ''
dataset_url2 = '' 

dataset = (0, dataset_url1, dataset_url2)

dataset_num = 0
count = 1

dataset_url = ''
clip_url = ''
cam = cv2.VideoCapture(clip_url)
cur_frame_index = 0


def init(dataset_index, start_video_index):
    global dataset_url
    global count
    global clip_url

    count = start_video_index
    dataset_url = dataset[dataset_index]

    # read video from camera or files
    if dataset_index > 0:
        clip_url = dataset_url + 'video (' + str(count) + ').avi'
        print clip_url
        cam = cv2.VideoCapture(clip_url)
        ret, frame = cam.read()

    else:
        cam = cv2.VideoCapture(0)


def release():
    if cam is not None:
        cam.release()


def get_next_frame():
    index = 0
    global cam
    global cur_frame_index
    global count
    global clip_url

    ret, frame = cam.read()

    if frame is None:
        if cur_frame_index == 0:
            count -= 1
        cur_frame_index = 0
        count += 1
        clip_url = dataset_url + 'video (' + str(count) + ').avi'
        if not os.path.isfile(clip_url):
            index = -1
            return None, index, 'video (' + str(count) + ').avi'
        else:
            cam = cv2.VideoCapture(clip_url)
            return get_next_frame()
    else:
        cv2.imshow("Originframe", frame)
        index = cur_frame_index
        cur_frame_index += 1
        resized = cv2.resize(frame, (320,240))
        return resized, index, 'video (' + str(count) + ').avi'
