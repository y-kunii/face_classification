# coding: UTF-8
#######################################################
# 
# HappyMirror で使用する定数定義
# 
#######################################################

LED_NUM             = 12        # LED の数（例：NeoPixel Ring→12、ラインLED(1m）→ 60）
LED_HEARTBEAT       = 0         # ハートビート用LEDの番号（最小値：0、LED_NUM未満にしてください。使わない場合はLED_NUM以上にしてください。）
LED_FACEDETECT      = 1         # 顔認識通知用LEDの番号（最小値：0、LED_NUM未満にしてください。使わない場合はLED_NUM以上にしてください。）

# Raspberry Pi 用 NeoPixel ライブラリ制御用定数
# 使用するピンや DMA 等を変更する場合、書き換えてください。
LED_PIN             = 18        # NeoPixel に接続する GPIO pin （PWMをサポートしていること）
LED_FREQ_HZ         = 800000    # LED 信号の周波数（Hz）
LED_DMA             = 5         # LED に 送信する信号を生成する DMA チャネル
LED_BRIGHTNESS      = 255       # LED の明るさ（0 ～ 255） 個別に変更するので、この定数は使いません。
LED_INVERT          = False     # NPN トランジスタレベルシフトを使う場合、信号を反転させるため True にします。

# 感情の数と、各感情に割り当てられた番号
EMOTION_NUM = 7             # 感情の数

EMOTION_ANGRY       = 0     # angry
EMOTION_DISGUST     = 1     # disgust
EMOTION_FEAR        = 2     # fear
EMOTION_HAPPY       = 3     # happy
EMOTION_SAD         = 4     # sad
EMOTION_SURPRISE    = 5     # surprise
EMOTION_NORMAL      = 6     # normal
#EMOTION_UNKNOWN     = 7     # その他／OFFするときなどに使用する

