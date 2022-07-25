# coding: UTF-8
#######################################################
#
# happymirror_voice.py
#
# HappyMirror 用音声出力
#
#######################################################
import time
import subprocess
import random
from happymirror_const import *

# 音声データの格納ディレクトリ
VOICE_DIR = '../voice/'

# 音声データ（ファイル名）のリスト
# [][0] = 顔検出時、[][1] = 笑顔が規定時間持続した時
voice_list = (
    ('004_waratte.wav',                 '002_online_ganbatte.wav'),             # 0
    ('005_egaomisete.wav',              '003_itterassyai.wav'),                 # 1
)


voice_no = 0            # 選択された音声データリストの番号

def play_voice(situation):
    """
    aplay をサブプロセスで実行して、voice で与えられた音源ファイルを再生します。
    voice_no : 音声データリストの中で再生するデータの要素番号
    situation: 状況（0 = 顔検出時 or 1 = 笑顔が規定時間持続した時）
    """
    global voice_no
    if situation > SITUATION_HAPPY_FULL:    # 引数が範囲外の時は音を出さずに終了します。
        return

    if situation == SITUATION_FACEDETECT:   # 笑顔を促すときにランダムでデータ番号を決めます。
        voice_no = random.randint(1, len(voice_list)) - 1

    print(f"play_voice: voice_no = {voice_no}, situation = {situation}")
    voice_file = VOICE_DIR + voice_list[voice_no][situation]
    print(f"play_voice: {voice_file}")
#    cp = subprocess.run(['sudo','-u' , '#1000', 'XDG_RUNTIME_DIR=/run/user/1000', 'aplay', voice])
    subprocess.Popen(['aplay', voice_file])
