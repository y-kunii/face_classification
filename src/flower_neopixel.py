# coding: UTF-8

import os
import time
import pickle
import base64
import numpy as np
import threading
#from threading import Semaphore, Thread
from neopixel import *
from happymirror_const import *

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=0):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms/1000.0)


# すべての LED を消灯する。
def all_led_off(strip):
    colorWipe(strip, Color(0, 0, 0))  # clear wipe


# LED を初期化する。
def init():
    global LED_NUM
    # Create NeoPixel object with appropriate configuration.
    strip = Adafruit_NeoPixel(LED_NUM, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    # Intialize the library (must be called once before other functions).
    strip.begin()
    all_led_off(strip)
    return strip

# 引数で渡された LED の色情報を元に NeoPixel LED を設定・点灯させる。
# leds[*][0] の「強さ」は使わない。
def show(strip, leds):
    for i in range(len(leds)):
        strip.setPixelColor(i, Color(leds[i][1][0], leds[i][1][1], leds[i][1][2]))
    strip.show()



# NeoPixel 12 Ring に合わせて、各感情に 2 個ずつ LED を割り当て、プルチックの感情の輪と同じ並びにする。
# ただし、プルチックからの警戒と敬愛は削除。
# normal は全ての LED を白に点灯させるので、LED の割り当ては無い。
EMOTION_TO_LEDNO = (
    (0, 1),             # 0: angry     → LED No. 0,  1 赤
    (10, 11),           # 1: disgust   → LED No.10, 11 紫
    (4, 5),             # 2: fear      → LED No. 4,  5 緑
    (2, 3),             # 3: happy     → LED No. 2,  3 黄色
    (8, 9),             # 4: sad       → LED No. 8,  9 青
    (6, 7),             # 5: surprise  → LED No. 6,  7 水色
    tuple(range(0, 12)) # 6: normal    → すべて 白   # (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11)
)


# 感情→色変換
# emotion_prediction の配列は LED_BASE_DATA と同じ感情の並びで構成されている。（ただし 0～6）
def emotion_color(emotion, prediction):
    global EMOTION_COLOR
    led_data = []
    led_data.append(prediction)
    led_color = []
    led_color.extend(EMOTION_COLOR[emotion])
    led_color = [int(d * prediction) for d in led_color]   # 確率を掛けて色の強弱してみます。
    led_data.append(led_color)
    return led_data


# 各 LED のデータを作成する。
# 形式： [ s, [r, g, b]] を LED 1 つ分のデータとする。これを LED の数だけリストにする。
#   s : 感情の強さ（0.0～1.0） ただし最大の感情だけを点灯し、輝度は変えないため、ここでは常に 1.0 とする。
#   r, g, b : 赤、緑、青の輝度（それぞれ 0 ～ 254。 255 は予約）
def make_led_data(emotion_rates):
    global LED_NUM
    global EMOTION_COLOR_LEDOFF    # LED を OFF にするときの EMOTION_COLOR リストの要素番号
    global EMOTION_TO_LEDNO        # 感情番号とNeoPixelのLED番号の対応
    EMOTINO_STRENGTH = 1.0
    top_index = np.argmax(emotion_rates)        # 最大の感情のインデックスを取得する
    leds = []

    for i in range(LED_NUM):
        led_data = []
        if i in EMOTION_TO_LEDNO[top_index]:
            led_data = emotion_color(top_index, EMOTINO_STRENGTH)      # ここでは「強さ」に相当する確率をすべて 1 にしてしまいます。（一番大きかった感情のLEDだけを点灯させるため）
        else:
            led_data = emotion_color(EMOTION_COLOR_LEDOFF, EMOTINO_STRENGTH)
        leds.append(led_data)

    return leds


# 受信したデータオブジェクトをデコードします。
def deserialize(read_data):
    emotions = pickle.loads(base64.b64decode(read_data))
#    stream = read_data.decode()
#    str_emotions = stream.split()
#    emotions = [float(r) for r in str_emotions]
    return emotions


def watchdog_reset(sem):
    global watchdog
    sem.acquire()
    watchdog = 0
    sem.release()

def watchdog_increment(sem):
    global watchdog
    sem.acquire()
    watchdog += 1
    sem.release()

def watchdog_set(sem, value):
    global watchdog
    sem.acquire()
    watchdog = value
    sem.release()


ALL_OFF_COMMAND = "alloff"

# 一定時間命令が来なければ消灯するコマンドを FIFO に送信します。
# スレッドとして実行されることを想定しています。
def watchdog_ledoff(sem, f):
    global ALL_OFF_COMMAND
    global watchdog
    print("WDT: Start")
    watchdog_reset(sem)
    while True:
        time.sleep(1)
        if watchdog < 0:    # 負の数になっていれば終了
            break
        watchdog_increment(sem)
        print("WDT:", watchdog)
        if watchdog >= 5:
            print("WDT: Send command")
            watchdog_reset(sem)
            with open(f, "wb") as fifo:
                message = ALL_OFF_COMMAND + '\r\n'
                fifo.write(message)
    print("WDT: End of thread")


#################################################
# メイン処理
#################################################
strip = init()      # NeoPixel の初期化、オブジェクト生成
# 感情検出プロセスから感情データを受け取るFIFOを生成。
fifopath = os.path.join('/home/pi/smartlife', 'emotionflowerfifo')
if os.path.isfile(fifopath) == True:
    os.remove(fifopath)
os.mkfifo(fifopath, 0o666)
os.chmod(fifopath, 0o666)

# 一定時間感情を検出しなければ、消灯命令を出すスレッドを起動します。
watchdog = 0
sem = threading.Semaphore(1)
watchdog_thread = threading.Thread(target=watchdog_ledoff, args=(sem, fifopath))
print("Starting WDT thread")
watchdog_thread.start()

# 感情データを受信して NeoPixel を制御するメインループ処理
while True:
    with open(fifopath, "rb") as fifo:
        read_line = fifo.read()

    if len(read_line) <= 0:
#            print("no data")
        break
#        print("read_line=", read_line)

    # 一定期間感情を認識しなかったら LED をすべて消灯します。
    if read_line[:len(ALL_OFF_COMMAND)] == ALL_OFF_COMMAND:
        all_led_off(strip)
        continue
    watchdog_reset(sem)

    emotions = deserialize(read_line)
#        print("emotions=", emotions)
    if emotions[0] == 99.99:   # 終了コードを受信
        watchdog_set(sem, -1)  # スレッドに終了を知らせます。
        break

    # LED データを作成して、NeoPixel を制御します。
    leds = make_led_data(emotions)
    print("leds = ", leds)
    show(strip, leds)

# 終了処理
watchdog_thread.join()      # ウォッチドッグスレッドが終了するのを待ちます。
all_led_off(strip)          # 終了時はすべて消灯します。
os.remove(fifopath)         # FIFO を削除します。
print("flower_neopixel end.")
