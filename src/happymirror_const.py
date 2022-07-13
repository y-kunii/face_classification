# coding: UTF-8
#######################################################
# 
# HappyMirror で使用する定数定義
# 
#######################################################

HEARTBEAT_HOLD_TIME     = 1.0   # ハートビートを維持する時間（単位：秒。小数で秒未満も設定可能）
FACEDETECT_HOLD_TIME    = 2.0   # 顔検出通知を維持する時間（単位：秒。小数で秒未満も設定可能）
HAPPY_KEEP_TIME         = 4.0   # 笑顔を持続してほしい時間（単位：秒。小数で秒未満も設定可能）
HAPPY_FACE_CHECK_TIME   = 0.1   # 笑顔チェック周期。この時間が経過する度にそれまでの笑顔の割合を判定。（単位：秒。小数で秒未満も設定可能）
EMOTION_ACCUM_COUNT     = 3     # 過去何回分の感情データを蓄えるか
ANIMATION_ITERATION     = 30    # 笑顔の持続時間が HAPPY_KEEP_TIME 以上になったときに LED をキラキラさせる回数（これで時間調整してください。）

LED_NUM             = 37        # LED の数（例：NeoPixel Ring→12、ラインLED(1m）→ 60）
LED_HEARTBEAT       = 0         # ハートビート用LEDの番号（最小値：0、LED_NUM未満にしてください。使わない場合はLED_NUM以上にしてください。）
LED_FACEDETECT      = 1         # 顔認識通知用LEDの番号（最小値：0、LED_NUM未満にしてください。使わない場合はLED_NUM以上にしてください。）

# emotion_prediction の順に並べた感情の色情報
EMOTION_COLOR = (
    # R    G    B
    ( 63,   0,   0),    #  0: angry
    ( 63,   0,  63),    #  1: disgust
    (  0,  63,   0),    #  2: fear
    ( 63,  63,   0),    #  3: happy
    (  0,   0,  63),    #  4: sad
    (  0,  63,  63),    #  5: surprise
    ( 15,  15,  15),    #  6: normal
    (  0,   0,   0),    #  OFF
    ( 20,  20,  20),    #  default
)
EMOTION_COLOR_LEDOFF  = 7   # LED を OFF にするときの EMOTION_COLOR リストの要素番号
EMOTION_COLOR_DEFAULT = 8   # 顔を検出したとき、笑顔以外の表情のときなどデフォルトの色

# 感情の数と、各感情に割り当てられた番号
# 割り当てられた番号は emotion_prediction の出力順を使っています。
EMOTION_NUM         = 7             # 感情の数

EMOTION_ANGRY       = 0             # angry
EMOTION_DISGUST     = 1             # disgust
EMOTION_FEAR        = 2             # fear
EMOTION_HAPPY       = 3             # happy
EMOTION_SAD         = 4             # sad
EMOTION_SURPRISE    = 5             # surprise
EMOTION_NORMAL      = 6             # normal
EMOTION_UNKNOWN     = EMOTION_NUM   # その他／OFFするときなどに使用する


# Raspberry Pi 用 NeoPixel ライブラリ制御用定数
# 使用するピンや DMA 等を変更する場合、書き換えてください。
LED_PIN             = 21        # NeoPixel に接続する GPIO pin （PWMをサポートしていること）
LED_FREQ_HZ         = 800000    # LED 信号の周波数（Hz）
LED_DMA             = 10         # LED に 送信する信号を生成する DMA チャネル
LED_BRIGHTNESS      = 255       # LED の明るさ（0 ～ 255） 個別に変更するので、この定数は使いません。
LED_INVERT          = False     # NPN トランジスタレベルシフトを使う場合、信号を反転させるため True にします。
LED_CHANNEL         = 0         # GPIO 13, 19, 41, 45 or 53 を使うときは 1 にします。

