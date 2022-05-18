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

from heartbeat import HeartBeat         # ハートビート用

# parameters for loading data and images
detection_model_path = '../trained_models/detection_models/haarcascade_frontalface_default.xml'
emotion_model_path = '../trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = get_labels('fer2013')


# 複数回の感情検出結果を元に LED の光らせ方を決める。
ANALYZE_COUNT = 3                   # 感情確率の和を保存する回数
EMOTION_NUM = 7                     # 感情の数
emotion_sum = [0.0] * EMOTION_NUM   # 7種類の感情ごとに確率の和を保存するリスト（「感情和リスト」と呼ぶ）
sum_count = 0                       # 感情和リストに加えた回数

# 感情和リストをリセットする。
def reset_emotion_sum():
    global EMOTION_NUM
    global emotion_sum
    global sum_count
    emotion_sum = [0.0] * EMOTION_NUM
    sum_count = 0


# 感情和リストに各感情の確率を加える。
def add_emotion_rate(emotion_prediction):
    global EMOTION_NUM
    global emotion_sum
    global sum_count
    for i in range(EMOTION_NUM):
        emotion_sum[i] += emotion_prediction[0][i]
    sum_count += 1


# 感情和リストの各要素の値を出力する（デバッグ用）
def print_emotion_sum():
    global EMOTION_NUM
    global emotion_sum
    for i in range(EMOTION_NUM):
        print("sum", i, ":", emotion_sum[i])


# 送信用にデータをエンコードします。
def encode_data(raw_data):
#    stream = ""
#    for r in raw_data:
#        stream += str(r)
#        stream += " "
    bin_data = pickle.dumps(raw_data, protocol=2)   # 通信相手が Python2 のため、protocol=2
    uu_en = base64.b64encode(bin_data)
    enc_value = b"" + uu_en + "\r\n".encode()  # オブジェクトをシリアル化
    return enc_value


# 感情データに合わせたデータを作成し、LED（Arduino）に送信する
def output_leds(emotion_rates, fifo):
    send_data = encode_data(emotion_rates)
#    print("send_data = ", send_data)
    with open(fifo, "wb") as s:
        s.write(send_data)


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

reset_emotion_sum()                                     # 感情和リストをリセット
time_before = time.time()                               # ループ直前の時刻を保存（デバッグ用）

heart = HeartBeat()                                     # ハートビートのインスタンスを生成
heart.init()

# flower_neopixel と通信するための名前付きパイプ
fifopath = os.path.join('/home/pi/smartlife', 'emotionflowerfifo')
# os.mkfifo(fifopath, 0o666)

# starting video streaming
cv2.namedWindow('window_frame')
video_capture = cv2.VideoCapture(0)
while True:
    bgr_image = video_capture.read()[1]
    gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
    heart.beat()                                        # カメラ画像の読み取りができればハートビートを打つ

    faces = detect_faces(face_detection, gray_image)

    for face_coordinates in faces:

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

        print(emotion_text,color,emotion_probability)

        # debug
        time_now = time.time()
        print("time span: ", (time_now - time_before))   # 前回からの経過時間
        time_before = time_now

        add_emotion_rate(emotion_prediction)        # 感情の確率を加算する
        if (sum_count >= ANALYZE_COUNT):            # 感情検出回数が一定数たまったら LED に出力する
            print_emotion_sum()                     # debug
            output_leds(emotion_sum, fifopath)
            reset_emotion_sum()
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

    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
    cv2.imshow('window_frame', bgr_image)
    #time.sleep(500/1000)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("END")
        end_message = [99.99] * EMOTION_NUM # 終了時に flower_neopixel.py に送るデータ
        output_leds(end_message, fifopath)
        break
video_capture.release()
cv2.destroyAllWindows()
