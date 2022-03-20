#!/bin/sh
# sudo python flower_neopixel.py &
cd ~/smartlife/camara/multi_camera
python num_of_camera.py | grep "camera_number 0"
cd ~/smartlife/camara/face_classification/src
#sudo `which python` video_emotion_color_demo.py
python video_emotion_color_demo.py