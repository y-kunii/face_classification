# coding: UTF-8
#######################################################
#
# happymirror_neopixel.py
#
# HappyMirror 用 NeoPixel LED 制御クラス
#
#######################################################
import time
from rpi_ws281x import PixelStrip, Color
from happymirror_const import *
from emotion import Emotion
from notifier import Notifier

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


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=20, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


class EmotionKeepTimer():
    """
    表情（笑顔）をキープしている時間を計算するクラス。
    ただし、表情の更新は set() で都度行う必要があります。（自動的に時間計算するわけではありません。）
    """
    def __init__(self):
        self.__emotion_start_time = 0   # 笑顔が始まった時刻。笑顔でないときは 0 にリセットします。

    def reset(self):
        """
        笑顔の開始時刻をリセットします。
        """
        self.__emotion_start_time = 0

    def set(self, emotion):
        if emotion == EMOTION_HAPPY:
            if self.__emotion_start_time == 0:          # 笑顔開始
                self.__emotion_start_time = time.time() # 現在の時刻を設定
            else:
                pass                                    # 笑顔が続いているときは何もしません。
        else:                                           # 笑顔でなくなったらタイマをリセットします。
            self.reset()

    def get_keep_time(self):
        """
        笑顔が続いている時間を返します。
        """
        if self.__emotion_start_time == 0:
            return 0
        else:
            return time.time() - self.__emotion_start_time

    def get_keep_level(self):
        """
        笑顔が継続してほしい時間に対する、継続時間の割合を返します。
        3秒続いてほしいところ、現時点で2秒続いていたら 2/3 = 0.666 を返します。
        3秒以上続いたら、1.0 を返します。
        """
        keep_time = self.get_keep_time()
        return min((keep_time / HAPPY_KEEP_TIME), 1.0)


class HappyMirrorLed:
    """
    HappyMirror の LED を制御するクラス。
    """
    def __init__(self):
        """
        コンストラクタ
        LED オブジェクトを生成し、初期化します。
        """
        # NeoPixel オブジェクトを生成します。
        self.__strip = PixelStrip(LED_NUM, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        # NeoPixel ライブラリを初期化します。（最初に一度だけ実行する必要があります。）
        self.__strip.begin()
        self.all_led_off()
        self.__last_check_time = 0                  # 最後に表情をチェックした時刻
        self.__happy_keep_timer = EmotionKeepTimer()
#        self.__leds = [[0, 0, 0] for _ in range(LED_NUM)]
        self.__leds = self.default_led_color()

    def __del__(self):
        """
        デストラクタ
        全ての LED を消灯します。
        """
        self.all_led_off()

    def __colorWipe(self, color, wait_ms = 0):
        """
        すべての LED を指定の色（color）で点灯（消灯）します。
        wait_ms で 1 つずつ徐々に光らせることができます。
        """
        for i in range(self.__strip.numPixels()):
            self.__strip.setPixelColor(i, color)
            self.__strip.show()
            time.sleep(wait_ms/1000.0)

    def __show(self, leds):
        """
        複数の LED を指定した色で点灯（消灯）します。
        __colorWipe() と異なり、一度に全ての LED に対し、同時にそれぞれ異なった色に制御します。
        leds には制御したい LED の数だけ色データを格納しておく必要があります。
        """
        for i, led in enumerate(leds):
            self.__strip.setPixelColor(i, Color(led[0], led[1], led[2]))
        self.__strip.show()

    def start_check(self):
        """
        笑顔のチェック時刻を初期設定します。
        """
        self.__last_check_time = time.time()

    def __is_check_time(self):
        """
        笑顔のチェック周期を過ぎているか確認します。
        戻り値：
        False : チェック周期に達していない
        True  : チェック周期以上経過している
        """
        lapse = time.time() - self.__last_check_time
        if lapse < HAPPY_FACE_CHECK_TIME:
            is_over = False
        else:
            is_over = True

        return is_over

    def all_led_off(self):
        """
        すべての LED を消灯します。
        """
        self.__colorWipe(Color(0, 0, 0))

    def default_led_color(self):
        """
        顔を検出したときや、笑顔以外の表情が強くなったときなど、
        デフォルトでは全てのLEDを白色に点灯させます。
        """
        leds = [EMOTION_COLOR[EMOTION_COLOR_DEFAULT] for _ in range(LED_NUM)]
        return leds


    def __make_led_data(self, index):
        """
        各 LED のデータを作成します。
        index で受け取った感情の番号に対応する LED が指定の色で光るようにリストデータを作成します。
        emotion_color() のデータ形式： [ s, [r, g, b]] を LED 1 つ分のデータとします。
        出力データ形式： [g, r, b] を LED 1 つ分のデータとします。
        これを LED の数だけリストにします。
            s : 感情の強さ（0.0～1.0） ただし最大の感情だけを点灯し、輝度は変えないため、ここでは常に 1.0 としています。
            g, r, b : 緑、赤、青の輝度（それぞれ 0 ～ 254。 255 は予約）
        """
        EMOTION_STRENGTH = 1.0
        leds = []

        for i in range(LED_NUM):
            led_data = []
            if i in EMOTION_TO_LEDNO[index]:
                led_data = emotion_color(index, EMOTION_STRENGTH)
            else:
                led_data = emotion_color(EMOTION_COLOR_LEDOFF, EMOTION_STRENGTH)
            leds.append(led_data[1])

        return leds

    def __make_happy_led_data(self, level):
        """
        ハッピーのレベルをラインLEDの点灯データに変換します。
        @param level 点灯するLEDの割合（0 ～ 1.0）
        """
        EMOTION_STRENGTH = 1.0
        leds = []

        happy_led_num = int(LED_NUM * level)
        for i in range(LED_NUM):
            led_data = []
            if i <= happy_led_num:
                led_data = emotion_color(EMOTION_HAPPY, EMOTION_STRENGTH)
            else:
                led_data = emotion_color(EMOTION_COLOR_LEDOFF, EMOTION_STRENGTH)
            leds.append(led_data[1])

        return leds

    def __merge_led_color(self, heart_beat : Notifier, face_detect : Notifier, emotion : Emotion, leds : list):
        """
        ハートビート、顔検出の情報から、対応する LED データを上書きします。
        """
        # TODO: 顔検出用 LED データを上書きします。
        # TODO: ハートビート用 LED データを上書きします。

#        return leds
        pass

    def depict(self, heart_beat : Notifier, face_detect : Notifier, emotion : Emotion):
        """
        引数で与えられた各インスタンスから情報を取得して LED を光らせます。
        @param heart_beat ハートビート用インスタンス
        @param face_detect 顔検出用インスタンス
        @param emotion 感情データ用インスタンス
        """
#        largest_index, _ = emotion.get_largest_emotion_queue()
#        leds = self.__make_led_data(largest_index)
#        print(f"__merge_led_color: leds = {leds}")      # debug

        # 頻繁に表情チェックすると値がバタつくので、少し間隔を置いて、定期的にチェックするようにします。
        # その間、emotion インスタンスにて表情データを積算してくれています。
        if self.__is_check_time() == True:              # チェック時間を経過したらチェックします。
            # 最後の表情チェック時刻を更新します。
            self.start_check()
            # 確率が一番高い表情を調べます。
            largest_index, _ = emotion.get_largest_emotion_queue()
            self.__happy_keep_timer.set(largest_index)  # 今の感情から笑顔が続いている時間を設定します。
            # 笑顔をキープしている時間を、レベル（MAXの時間に対するキープ時間の割合 0.0～1.0）を取得します。
            keep_level = self.__happy_keep_timer.get_keep_level()
            # キープレベルから LED データに変換します。
            self.__leds = self.__make_happy_led_data(keep_level)
            # キープレベルが1.0（MAX）になったらレインボー表示します。
            if keep_level >= 1.0:
                theaterChaseRainbow(self.__strip)
                self.__happy_keep_timer.reset()     # 笑顔継続時間をリセットします。
                emotion.reset()                     # レインボー後は感情データをリセットします。

        # leds（LED データのリスト）を渡して、顔検出とハートビート情報を上書きします。
        self.__merge_led_color(heart_beat, face_detect, emotion, self.__leds)
        print(f"LED: {self.__leds}")                        # debug
        self.__show(self.__leds)

