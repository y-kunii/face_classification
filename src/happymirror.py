# coding: UTF-8

from statistics import mode

import cv2
import time
from keras.models import load_model
import numpy as np
import os
import pickle
import base64

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input

# ADD kuni
import json
import requests
import time
from datetime import datetime as dt

from notifier import Notifier           # ハートビート、顔検出通知用
from emotion import Emotion             # 感情データ処理用
from happymirror_const import *
from happymirror_neopixel import HappyMirrorLed # LED 制御用

# parameters for loading data and images
detection_model_path = '../trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = '../trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = get_labels('fer2013')

# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
face_detection = load_detection_model(detection_model_path)
emotion_classifier = load_model(emotion_model_path, compile=False)

# getting input model shapes for inference
emotion_target_size = emotion_classifier.input_shape[1:3]

# starting lists for calculating modes
emotion_window = []

time_before = time.time()                               # ループ直前の時刻を保存（デバッグ用）

heartbeat_notifier = Notifier(HEARTBEAT_HOLD_TIME)      # ハートビートのインスタンスを生成
face_detect_notifier = Notifier(FACEDETECT_HOLD_TIME)   # 顔検出通知用インスタンスを生成
emotion_data = Emotion()                                # 感情データ処理用インスタンスを生成。
happy_led = HappyMirrorLed()                            # HappyMirror 用 NeoPixel LED 制御インスタンスを生成

# starting video streaming
cv2.namedWindow('window_frame')
video_capture = cv2.VideoCapture(0)
heartbeat_notifier.init()                               # ハートビート初期化
face_detect_notifier.init()                             # 顔検出通知を初期化
happy_led.all_led_off()                                 # 念のため LED をすべて消灯します。

while True:
    bgr_image = video_capture.read()[1]
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    heartbeat_notifier.notice()                         # カメラ画像の読み取りができればハートビートを打つ

    faces = detect_faces(face_detection, gray_image)
    if len(faces) == 0:
        emotion_data.no_faces()                         # 顔を検出していない情報を emotion_data に知らせる。

    face_num = 0
    for face_coordinates in faces:
        # 一番大きい顔を取得し、その値が 100 以上なら表情判定に進みます。
        # それ以外は遠くの人や横から覗いている人と考えて、無視するようにします。
        # 展示会で多くの人を認識したり、遠くのパネルなどの誤認識をはじくため。
        # face_coordinates はそれぞれ以下のようなリストになっていて、[X座標, Y座標, サイズ, サイズ] のようなので、
        # 3 番目の要素 face_coordinates[2] を大きさの判定材料にします。
        # [239 230 132 132]
        # [222 326  53  53]
#        print(face_coordinates)
        if face_coordinates[2] < 100:
            continue

        face_num += 1
        face_detect_notifier.notice()                   # 顔を検出したら通知する。

        x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
        gray_face = gray_image[y1:y2, x1:x2]
        try:
            gray_face = cv2.resize(gray_face, (emotion_target_size))
        except:
            continue

        #pred_time_now = time.time()
        gray_face = preprocess_input(gray_face, True)
        gray_face = np.expand_dims(gray_face, 0)
        gray_face = np.expand_dims(gray_face, -1)
        emotion_prediction = emotion_classifier.predict(gray_face)
        emotion_probability = np.max(emotion_prediction)
        emotion_label_arg = np.argmax(emotion_prediction)
        emotion_text = emotion_labels[emotion_label_arg]
        #pred_time_before = time.time()
        #print("pred_timetime span: ", (pred_time_before - pred_time_now))   # 認識時間

#        # for debug
#        for i in range(len(emotion_prediction[0])):
#            print(str(i), emotion_labels[i], emotion_prediction[0][i])

        emotion_window.append(emotion_text)

        if len(emotion_window) > frame_window:
            emotion_window.pop(0)
        try:
            emotion_mode = mode(emotion_window)
        except:
            continue

        # 赤
        if emotion_text == 'angry':
            #color = emotion_probability * np.asarray((255, 0, 0))
            color = np.asarray((254, 0, 0))
        # 青
        elif emotion_text == 'sad':
            #color = emotion_probability * np.asarray((0, 0, 255))
            color = np.asarray((0, 0, 254))
        # 黄
        elif emotion_text == 'happy':
            #color = emotion_probability * np.asarray((255, 255, 0))
            color = np.asarray((254, 254, 0))
        # 水色
        elif emotion_text == 'surprise':
            #color = emotion_probability * np.asarray((0, 255, 255))
            color = np.asarray((0, 254, 254))
        # 紫
        elif emotion_text == 'disgust':
            #color = emotion_probability * np.asarray((128, 0, 128))
            color = np.asarray((128, 0, 128))
        # 緑 
        elif emotion_text == 'fear':
            #color = emotion_probability * np.asarray((0, 128, 0))
            color = np.asarray((0, 128, 0))
        # 白
        elif emotion_text == 'neutral':
            #color = emotion_probability * np.asarray((255, 255, 255))
            color = np.asarray((254, 254, 254))
        # defalt 黄緑 ここには、入らない。
        else:
            color = emotion_probability * np.asarray((0, 254, 0))

#        print(emotion_text,color,emotion_probability)

        # debug
        time_now = time.time()
#        print("time span: ", (time_now - time_before))   # 前回からの経過時間
        time_before = time_now

        # 感情値（各感情の確率）を蓄積します。
        # EmotionFlower の add_emotion_rate() と同じような役割をします。
        emotion_data.accumurate(emotion_prediction[0])

        #     # ADD kuni
        #     url = "https://script.google.com/macros/s/AKfycbwplNBc3ILI7VaPeYWTKmOZuW8pihMEgEvIGIMsQuVwXLs-5a93qzy8YfWvlXd1U3E_yw/exec"
        #     tdatetime = dt.now()
        #     tstr = (tdatetime.now().strftime('%Y/%m/%d %H:%M:%S:%f')[:-3])
        #     # print(tstr)
        #     # JSON形式でデータを用意してdataに格納
        #     data = {
        #     	"timestamp": tstr,
        #     	"emotion"  : emotion_text,
        #     	"other"    : str(emotion_probability)
        #     }
        #     # json.dumpでデータをJSON形式として扱う
        #     r = requests.post(url, data=json.dumps(data))

        color = color.astype(int)
        color = color.tolist()

        draw_bounding_box(face_coordinates, rgb_image, color)
        draw_text(face_coordinates, rgb_image, emotion_text,
                  color, 0, -45, 1, 1)

        # ウィンドウ全体に太い枠を描画します。
        THICKNESS = 20
        height, width = rgb_image.shape[:2]
        cv2.rectangle(rgb_image, (0 + THICKNESS, 0 + THICKNESS), (width - THICKNESS, height - THICKNESS), color, thickness=20)

    if face_num == 0:
        emotion_data.no_faces()                         # 顔が小さい（遠くにいる）ときは、検出なし扱いとします。

    # LED を制御します。
    # for ブロックの中は顔を検出されないと実行されないので、for の外で行います。
    happy_led.depict(heartbeat_notifier, face_detect_notifier, emotion_data)

    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    cv2.imshow('window_frame', bgr_image)
    #time.sleep(500/1000)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video_capture.release()
cv2.destroyAllWindows()
