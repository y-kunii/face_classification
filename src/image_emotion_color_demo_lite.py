from statistics import mode

import cv2
#from keras.models import load_model
from tflite_runtime.interpreter import Interpreter
import numpy as np

from utils.datasets import get_labels
from utils.inference import detect_faces
from utils.inference import draw_text
from utils.inference import draw_bounding_box
from utils.inference import apply_offsets
from utils.inference import load_detection_model
from utils.preprocessor import preprocess_input
import time

# parameters for loading data and images
detection_model_path = '../trained_models/detection_models/haarcascade_frontalface_default.xml'
#emotion_model_path = '../trained_models/emotion_models/fer2013_mini_XCEPTION.102-0.66.hdf5'
emotion_labels = get_labels('fer2013')

# hyper-parameters for bounding boxes shape
frame_window = 10
emotion_offsets = (20, 40)

# loading models
face_detection = load_detection_model(detection_model_path)
#emotion_classifier = load_model(emotion_model_path, compile=False)
interpreter = Interpreter(model_path="output.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# getting input model shapes for inference
#emotion_target_size = emotion_classifier.input_shape[1:3]
emotion_target_size = input_details[0]['shape'][1:3]
print(emotion_target_size)
# starting lists for calculating modes
emotion_window = []

bgr_image = cv2.imread('../sample/test2.jpg')
gray_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
rgb_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2RGB)
faces = detect_faces(face_detection, gray_image)

for face_coordinates in faces:
    x1, x2, y1, y2 = apply_offsets(face_coordinates, emotion_offsets)
    gray_face = gray_image[y1:y2, x1:x2]
    try:
        gray_face = cv2.resize(gray_face, (tuple(emotion_target_size)))
    except:
        continue
    gray_face = preprocess_input(gray_face, True)
    gray_face = np.expand_dims(gray_face, 0)
    gray_face = np.expand_dims(gray_face, -1)

    #emotion_prediction = emotion_classifier.predict(gray_face)
    start = time.time()
    input_shape = input_details[0]['shape']
    input_data = np.reshape(gray_face, input_shape)
    interpreter.set_tensor(input_details[0]['index'], np.array(input_data, dtype=np.float32))
    interpreter.invoke()
    emotion_prediction = interpreter.get_tensor(output_details[0]['index'])
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time) + "[sec]")
    emotion_probability = np.max(emotion_prediction)
    emotion_label_arg = np.argmax(emotion_prediction)
    emotion_text = emotion_labels[emotion_label_arg]
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
    color = color.astype(int)
    color = color.tolist()
    draw_bounding_box(face_coordinates, rgb_image, color)
    draw_text(face_coordinates, rgb_image, emotion_text,
              color, 0, -45, 1, 1)
bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
cv2.imwrite('../sample/test2_emotion.jpg', bgr_image)

