from django.test import TestCase
import unittest
# from subprocess
from subprocess import call

# from utils import jj, profile
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")
from django.conf import settings
import cv2
import numpy as np
from style_transfer.style_transfer import StyleTransfer
from PIL import Image
# from keyframes.keyframes import KeyFramesExtractor
import uuid


def jj(*args):
    return os.path.join(*args)


def post_precess(img, wh):
    img = (img.squeeze() + 1.) / 2 * 255
    img = img.astype(np.uint8)
    img = cv2.resize(img, (wh[0], wh[1]))
    return img


def save(frame, name):
    path = 'media/comic/'
    img_name = name + '.png'
    img = Image.fromarray(frame.astype('uint8'))  # convert image to uint8:  frame.astype('uint8')
    img.save(path + img_name)


def cartoon(img_rgb):
    img_color = img_rgb
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 7)
    img_edge = cv2.adaptiveThreshold(img_blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, blockSize=9, C=2)
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
    img_cartoon = cv2.bitwise_and(img_color, img_edge)
    return img_cartoon


def video2comix(style_transfer_mode=1):
    inputmp4 = jj(settings.TMP_DIR, 'f1_short.mp4')
    outputmp4 = jj('media/comic/', 'f1_short_comi.mp4')
    outputh264 = jj('media/comic/', 'f1_short_comi_h264.mp4')
    # outputmp4 = jj(settings.TMP_DIR, 'f1_short_comi.mp4')
    vc = cv2.VideoCapture(inputmp4)  # self.file.path
    print('open status:', vc.isOpened())
    fps = vc.get(cv2.CAP_PROP_FPS)
    fps_flow = 3  # fps / 2
    # MPEG can not play in web
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    wh = (452, 252)
    flow_video = cv2.VideoWriter(outputmp4, fourcc, fps_flow, wh)
    i = 0
    imgname = uuid.uuid4().hex
    while vc.isOpened():
        su, frame = vc.read()
        if frame is None:
            print('video2comix - read frame is none')
            break
        if su:
            # transform frame 2 comix
            # 风格化处理
            frames = []
            frames.append(frame)
            stylized_keyframes, stylization_time = StyleTransfer.get_stylized_frames(frames=frames,
                                                                                     style_transfer_mode=style_transfer_mode)

            save(frame, imgname + str(i));
            if i == 0:
                save(stylized_keyframes[0], imgname + str(i) + "_c");
            cimg = cartoon(frame)
            save(cimg, imgname + str(i) + "_carton")

            img = stylized_keyframes[0].astype('uint8')
            # img=post_precess(img,wh)

            flow_video.write(img)
            # flow_video.write(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
            # cv2.waitKey(1)
            i = i + 1
            if i > 6:
                break
    print('video saved.')
    call(["ffmpeg", "-i", outputmp4, "-vcodec", "libx264", "-f", "mp4", outputh264])
    print('finish')
    flow_video.release()
    vc.release()
    return 0


class HelloTest(unittest.TestCase):
    def test_hello_name(self):
        hello_str = video2comix(1)
        self.assertEqual(hello_str, 0)


unittest.main()